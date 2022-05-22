from email.policy import default
import requests
from arkid.config import get_app_config
from oauth2_provider.models import Application
from django.conf import settings
import datetime
import uuid
from arkid.core.models import User, App
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.db import transaction


arkid_saas_token_cache = {}

def get_saas_token(tenant, token):
    """
    获取saas平台token
    """
    # 缓存 saas_token
    key = (tenant.id, token)
    if key in arkid_saas_token_cache:
        return arkid_saas_token_cache[key]
    app = Application.objects.filter(name='arkid_saas').first()
    host = get_app_config().get_host()
    url = f"{host}/api/v1/tenant/{tenant.id.hex}/oauth/authorize/"
    nonce = uuid.uuid4().hex
    params = {
        "client_id": app.client_id,
        "redirect_uri": app.redirect_uris,
        "scope": "openid",
        "response_type": "code",
        "token": token,
        "response_type": "id_token",
        "state": "",
        "nonce": nonce,
        "response_mode": "query",
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        arkid_saas_token_cache.pop(key, None)
        raise Exception(f'Error get_saas_token: {resp.status_code}')
    resp = resp.json()
    arkid_saas_token_cache[key] = (resp['token'], resp['tenant_id'], resp['tenant_slug'])
    return arkid_saas_token_cache[key]


arkstore_access_token_cache = {}

def get_arkstore_access_token(tenant, token):
    """
    获取插件商店access_token
    """
    # 缓存 idtoken
    key = (tenant.id, token)
    if key in arkstore_access_token_cache:
        return arkstore_access_token_cache[key]
    saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token)
    params = {'state': 'client', 'tenant_slug': saas_tenant_slug, 'tenant_uuid': saas_tenant_id,'token': saas_token}
    app_login_url = settings.ARKSTOER_URL + '/api/v1/login'
    resp = requests.get(app_login_url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_access_token: {resp.status_code}')
    resp = resp.json()
    arkstore_access_token_cache[key] = resp['access_token']
    return arkstore_access_token_cache[key] 


def get_arkstore_extensions(access_token, purchased=None, offset=0, limit=10):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions?offset={offset}&limit={limit}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    if purchased is not None:
        params['purchased'] = purchased
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extensions: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_apps(access_token, purchased=None, offset=0, limit=10):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps?offset={offset}&limit={limit}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    if purchased is not None:
        params['purchased'] = purchased
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_apps: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_apps_and_extensions(access_token, purchased=None, offset=0, limit=10):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps_and_extensions?offset={offset}&limit={limit}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    if purchased is not None:
        params['purchased'] = purchased
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_apps_and_extensions: {resp.status_code}')
    resp = resp.json()
    return resp


def purcharse_arkstore_extension(access_token, extension_id):
    order_url = settings.ARKSTOER_URL + '/api/v1/user/orders'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'extension_uuid': extension_id
    }
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error purcharse_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def lease_arkstore_extension(access_token, extension_id):
    order_url = settings.ARKSTOER_URL + '/api/v1/user/lease'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'extension_uuid': extension_id
    }
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error lease_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_detail(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/extensions/{extension_id}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_detail: {resp.status_code}')
    resp = resp.json()
    return resp


def install_arkstore_extension(tenant, token, extension_id):
    access_token = get_arkstore_access_token(tenant, token)
    res = get_arkstore_extension_detail(access_token, extension_id)
    if res['type'] == 'oidc':
        app = get_arkid_saas_app_detail(tenant, token, extension_id)
        create_tenant_oidc_app(tenant, app['url'], app['name'], app['description'], app['logo'])
    elif res['type'] == 'auto_form_fill':
        app = get_arkid_saas_app_detail(tenant, token, extension_id)
        app['data'] = {}
        create_tenant_app(tenant, app)
    elif res['type'] == 'extension':
        download_arkstore_extension(tenant, token, extension_id, res)
    else:
        raise Exception(f"unkown arkstore app and extension type: res['type']")


def download_arkstore_extension(tenant, token, extension_id, extension_detail):
    from arkid import config
    from pathlib import Path
    access_token = get_arkstore_access_token(tenant, token)
    extension_name = extension_detail['name']

    app_config = config.get_app_config()
    extension_root = app_config.extension.config.get('install_dir') or app_config.extension.root[0]

    download_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/download'
    headers = {'Authorization': f'Token {access_token}'}
    resp = requests.get(download_url, headers=headers)
    if resp.status_code == 402:
        resp = resp.json()
        raise Exception(f"error: download failed, msg: {resp.get('msg')}")
    if resp.status_code != 200:
        raise Exception('error: download failed')

    # delete extension folder
    folder_name = Path(extension_root) / extension_name
    import shutil
    if folder_name.exists():
        try:
            shutil.rmtree(folder_name)
        except OSError as e:
            print ("Error remove folder: %s - %s." % (e.filename, e.strerror))
            return {'error': 'delete extension fodler failed'}

    # unzip
    import zipfile
    import io
    extract_folder = Path(extension_root)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zip_ref:
        zip_ref.extractall(extract_folder)

    return {'success': 'true'}


def get_bind_arkstore_agent(access_token):
    order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
    resp = resp.json()
    return resp


def bind_arkstore_agent(access_token, tenant_slug):
    order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'tenant_slug': tenant_slug
    }
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
    resp = resp.json()
    return resp


def change_arkstore_agent(access_token, tenant_slug):
    order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'tenant_slug': tenant_slug
    }
    resp = requests.put(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
    resp = resp.json()
    return resp


def unbind_arkstore_agent(access_token):
    order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.delete(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
    resp = resp.json()
    return resp


def create_tenant_oidc_app(tenant, url, name, description='', logo=''):
    app, created = App.objects.get_or_create(
            tenant=tenant,
            name=name,
            url=url,
            defaults={"description": description, "logo": logo,}
        )
    return app


@transaction.atomic()
def create_tenant_app(tenant, saas_app):
    from arkid.core.event import Event, register_event, dispatch_event
    from arkid.core.event import(
        CREATE_APP, UPDATE_APP, DELETE_APP,
        CREATE_APP_DONE, SET_APP_OPENAPI_VERSION,
    )
    defaults = {
        "name": saas_app['name'],
        "logo": saas_app['logo'],
        "type": saas_app['type'],
        "url": saas_app['url'],
        "package": saas_app['package'], 
        "description": saas_app['description'], 
    }
    app, created = App.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name=saas_app['name'],
            type=saas_app['type'],
            # url=saas_app['url'],
            defaults=defaults
        )
    if not created:
        return app

    # results = dispatch_event(Event(tag=CREATE_APP, tenant=tenant, data=saas_app))
    # for func, (result, extension) in results:
    #     if result:
    #         # 创建config
    #         config = extension.create_tenant_config(tenant, saas_app['config'], saas_app.name, saas_app['type'])
    #         # update app
    #         app.config = config
    #         app.save()
    #         # 创建app完成进行事件分发
    #         dispatch_event(Event(tag=CREATE_APP_DONE, tenant=tenant, data=app))
    #         break

    return app

    
def get_arkid_saas_app_detail(tenant, token, extension_id):
    saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token)
    arkid_saas_app_url = settings.ARKID_SAAS_URL + f'/api/v1/com_longgui_arkid_saas/tenant/{saas_tenant_id}/arkid/saas/app/{extension_id}/'
    headers = {'Authorization': f'Token {saas_token}'}
    params = {}
    resp = requests.get(arkid_saas_app_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_detail: {resp.status_code}')
    resp = resp.json()
    return resp


arkstore_access_token_saas_cache = {}

def get_arkstore_access_token_with_saas_token(tenant, token):
    """
    获取插件商店access_token
    """
    # 缓存 idtoken
    key = (tenant.id, token)
    if key in arkstore_access_token_saas_cache:
        return arkstore_access_token_saas_cache[key]
    params = {'state': 'client', 'tenant_slug': tenant.slug, 'tenant_uuid': tenant.id.hex, 'token': token}
    app_login_url = settings.ARKSTOER_URL + '/api/v1/login'
    resp = requests.get(app_login_url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_access_token: {resp.status_code}')
    resp = resp.json()
    arkstore_access_token_saas_cache[key] = resp['access_token']
    return arkstore_access_token_saas_cache[key] 


def check_arkstore_purchased(tenant, token, app):
    access_token = get_arkstore_access_token_with_saas_token(tenant, token)
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps/saas_app_order/{app.id.hex}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(order_url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise Exception(f'Error check_arkstore_purchased: {resp.status_code}')
    resp = resp.json()
    if resp.get("use_end_time") == '0':
        return True
    if resp.get("use_end_time") is not None:
        use_end_time = parse_datetime(resp["use_end_time"])
        if use_end_time <= timezone.now():
            return True
    if resp.get("max_users"):
        count = len(User.active_objects.filter(tenant=tenant).all())
        if resp.get("max_users") is not None and resp.get("max_users") <= count:
            return True
    return False


def check_arkstore_expired(tenant, token, package_idendifer):
    access_token = get_arkstore_access_token(tenant, token)
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/order/'
    headers = {'Authorization': f'Token {access_token}'}
    params = {'package_idendifer': package_idendifer}
    resp = requests.get(order_url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f'Error check_arkstore_expired: {resp.status_code}')
        return True
    resp = resp.json()
    if resp.get("use_end_time") == '0':
        return True
    if resp.get("use_end_time") is not None:
        use_end_time = parse_datetime(resp["use_end_time"])
        if use_end_time <= timezone.now():
            return True
    if resp.get("max_users"):
        count = len(User.active_objects.filter(tenant=tenant).all())
        if resp.get("max_users") is not None and resp.get("max_users") <= count:
            return True
    return False