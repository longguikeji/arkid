import requests
from app.models import App
from config import get_app_config
from oauth2_provider.models import Application
from runtime import get_app_runtime
from django.conf import settings
import datetime
from inventory.models import User
from django.utils.dateparse import parse_datetime
from django.utils import timezone


arkid_saas_token_cache = {}

def get_saas_token(tenant, token):
    """
    获取saas平台token
    """
    # 缓存 saas_token
    key = (tenant.uuid, token)
    if key in arkid_saas_token_cache:
        return arkid_saas_token_cache[key]
    app = Application.objects.filter(name='arkid_saas').first()
    host = get_app_config().get_host()
    url = f"{host}/api/v1/tenant/{tenant.uuid.hex}/oauth/authorize/"
    params = {
        "client_id": app.client_id,
        "redirect_uri": app.redirect_uris,
        "scope": "openid",
        "response_type": "code",
        "token": token,
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_saas_token: {resp.status_code}')
    resp = resp.json()
    arkid_saas_token_cache[key] = (resp['token'], resp['tenant_uuid'], resp['tenant_slug'])
    return arkid_saas_token_cache[key]


arkstore_access_token_cache = {}

def get_arkstore_access_token(tenant, token):
    """
    获取插件商店access_token
    """
    # 缓存 idtoken
    key = (tenant.uuid, token)
    if key in arkstore_access_token_cache:
        return arkstore_access_token_cache[key]
    saas_token, saas_tenant_uuid, saas_tenant_slug = get_saas_token(tenant, token)
    params = {'state': 'client', 'tenant_slug': saas_tenant_slug, 'token': saas_token}
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


def purcharse_arkstore_extension(access_token, extension_uuid):
    order_url = settings.ARKSTOER_URL + '/api/v1/user/orders'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'extension_uuid': extension_uuid
    }
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error purcharse_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_detail(access_token, extension_uuid):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/extensions/{extension_uuid}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_detail: {resp.status_code}')
    resp = resp.json()
    return resp


def install_arkstore_extension(tenant, token, extension_uuid):
    access_token = get_arkstore_access_token(tenant, token)
    res = get_arkstore_extension_detail(access_token, extension_uuid)
    if res['type'] == 'oidc':
        app = get_arkid_saas_app_detail(tenant, token, extension_uuid)
        create_tenant_oidc_app(tenant, app['url'], app['name'], app['description'], app['logo'])
    elif res['type'] == 'auto_form_fill':
        app = get_arkid_saas_app_detail(tenant, token, extension_uuid)
        app['data'] = {}
        create_tenant_app(tenant, app)
    elif res['type'] == 'extension':
        download_arkstore_extension(tenant, token, extension_uuid, res)
    else:
        raise Exception(f"unkown arkstore app and extension type: res['type']")


def download_arkstore_extension(tenant, token, extension_uuid, extension_detail):
    import config
    from pathlib import Path
    access_token = get_arkstore_access_token(tenant, token)
    extension_name = extension_detail['name']

    app_config = config.get_app_config()
    extension_root = app_config.extension.root

    download_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_uuid}/download'
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


def create_tenant_oidc_app(tenant, url, name, description='', logo=''):
    protocol_type = 'OIDC'
    app, created = App.objects.get_or_create(
            tenant=tenant,
            name=name,
            type=protocol_type,
            url=url,
            defaults={"description": description, "logo": logo,}
        )
    if not created:
        return app

    r = get_app_runtime()
    provider_cls = r.app_type_providers.get(protocol_type, None)
    assert provider_cls is not None
    provider = provider_cls()
    protocol_data = {
        "skip_authorization": False,
        "redirect_uris": "",
        "client_type": "public",
        "grant_type": "authorization-code",
        "algorithm": "",
    }
    data = provider.create(app=app, data=protocol_data)
    if data is not None:
        app.data = data
        app.save()
    return app


def create_tenant_app(tenant, saas_app):
    app, created = App.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name=saas_app['name'],
            type=saas_app['type'],
            # url=saas_app['url'],
            defaults={"description": saas_app['description'], "logo": saas_app['logo']}
        )

    r = get_app_runtime()
    provider_cls = r.app_type_providers.get(saas_app['type'], None)
    assert provider_cls is not None
    provider = provider_cls()
    protocol_data = saas_app.get('data', {})
    data = provider.create(app=app, data=protocol_data)
    if data is not None:
        app.data = data
        app.save()
    return app

    
def get_arkid_saas_app_detail(tenant, token, extension_uuid):
    saas_token, saas_tenant_uuid, saas_tenant_slug = get_saas_token(tenant, token)
    arkid_saas_app_url = settings.ARKID_SAAS + f'/api/v1/tenant/{saas_tenant_uuid}/arkid/saas/app'
    headers = {'Authorization': f'Token {saas_token}'}
    params = {'extension_uuid': extension_uuid}
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
    key = (tenant.uuid, token)
    if key in arkstore_access_token_saas_cache:
        return arkstore_access_token_saas_cache[key]
    params = {'state': 'client', 'tenant_slug': tenant.slug, 'token': token}
    app_login_url = settings.ARKSTOER_URL + '/api/v1/login'
    resp = requests.get(app_login_url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_access_token: {resp.status_code}')
    resp = resp.json()
    arkstore_access_token_saas_cache[key] = resp['access_token']
    return arkstore_access_token_saas_cache[key] 


def check_arkstore_purchased(tenant, token, app):
    access_token = get_arkstore_access_token_with_saas_token(tenant, token)
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps/saas_app_order/{app.uuid.hex}'
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
        count = len(User.active_objects.filter(tenants=tenant).all())
        if resp.get("max_users") is not None and resp.get("max_users") <= count:
            return True
    return False
