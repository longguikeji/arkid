from email.policy import default
import requests
from arkid.config import get_app_config
from arkid.core import extension
from oauth2_provider.models import Application
from django.conf import settings
from datetime import datetime
import jwt
import uuid
from arkid.core.models import User, App
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.db import transaction
from arkid.core.models import Tenant
from arkid.extension.models import TenantExtension, Extension
from arkid.extension.utils import import_extension, unload_extension, load_extension_apps, restart_celery
from pathlib import Path
from arkid.common.logger import logger
from django.core.cache import cache


def get_saas_token(tenant, token, use_cache=True):
    """
    获取saas平台token
    """
    # 缓存 saas_token
    key = (str(tenant.id) + '_' + str(token)).replace('-', '')
    saas_cache = cache.get(key)
    if use_cache and saas_cache:
        return saas_cache

    app = Application.objects.filter(name='arkid_saas', uuid = tenant.id).first()
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

    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('somepage.html', data=params)
    request.tenant = tenant
    from arkid.core.models import ExpiringToken
    token = ExpiringToken.objects.get(token=token)
    request.user = token.user
    from oauth2_provider.views.base import AuthorizationView
    resp = AuthorizationView.as_view()(request)
    assert resp.status_code == 302

    resp = requests.get(resp.url)
    if resp.status_code != 200:
        cache.delete(key)
        raise Exception(f'Error get_saas_token: {resp.status_code}')
    resp = resp.json()
    result = (resp['token'], resp['tenant_id'], resp['tenant_slug'])
    # 中心arkid token 24小时过期
    cache.set(key, result, timeout=60*60*23)
    return result


def get_arkstore_access_token(tenant, token, use_cache=True):
    """
    获取插件商店access_token
    """
    try:
        saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token, use_cache=use_cache)
        return get_arkstore_access_token_with_saas_token(saas_tenant_slug, saas_tenant_id, saas_token, 
            use_cache=use_cache, local_tenant=tenant, local_token=token)
    except Exception as e:
        logger.error(f'get_arkstore_access_token failed: {str(e)}, give it a retry')
        saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token, use_cache=False)
        return get_arkstore_access_token_with_saas_token(saas_tenant_slug, saas_tenant_id, saas_token, 
            use_cache=False, local_tenant=tenant, local_token=token)



def get_arkstore_access_token_with_saas_token(saas_tenant_slug, saas_tenant_id, saas_token, 
        use_cache=True, local_tenant=None, local_token=None):
    """
    获取插件商店access_token
    """
    # 缓存 idtoken
    key = (str(saas_tenant_id) + '_' + str(saas_token)).replace('-', '')
    id_token = cache.get(key)
    if use_cache and id_token:
        try:
            payload = jwt.decode(id_token, options={"verify_signature": False})
        except Exception:
            cache.delete(key)
            raise Exception("Unable to parse id_token")
        exp_dt = datetime.fromtimestamp(payload["exp"])
        expire_time = timezone.make_aware(exp_dt, timezone.get_default_timezone())
        now = timezone.localtime()
        if now <= expire_time:
            return id_token
        else:
            cache.delete(key)
            # id_token 过期后，重新获取saas_token和id_token
            if local_tenant and local_token:
                saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(local_tenant, local_token, use_cache=False)
    
    params = {'state': 'client', 'tenant_slug': saas_tenant_slug, 'tenant_id': str(saas_tenant_id), 'token': saas_token}
    app_login_url = settings.ARKSTOER_URL + '/api/v1/login'
    resp = requests.get(app_login_url, params=params)
    if resp.status_code != 200:
        cache.delete(key)
        raise Exception(f'Error get_arkstore_access_token_with_saas_token: {resp.status_code}, url: {resp.url}')
    try:
        resp = resp.json()
    except:
        from urllib.parse import urlencode, unquote
        raise Exception(f'Error get_arkstore_access_token_with_saas_token: {resp.status_code}, url: {unquote(resp.url)}')
    id_token = resp['access_token']
    # arkstore idtoken 10小时过期
    cache.set(key, id_token, timeout=60*60*9)
    return id_token


def get_arkstore_extensions(access_token, purchased=None, rented=False, type=None, offset=0, limit=10, extra_params={}):
    if type == 'extension':
        if rented:
            url = "/api/v1/arkstore/extensions/leased"
        else:
            url = '/api/v1/arkstore/extensions/purchased'
    elif type == 'app':
        url = '/api/v1/arkstore/apps/purchased'
    elif type == 'private_app':
        url = '/api/v1/arkstore/private_apps/purchased'
    elif type == 'category':
        url = '/api/v1/arkstore/app/categories'
    else:
        url = '/api/v1/arkstore/apps_and_extensions'
    arkstore_extensions_url = settings.ARKSTOER_URL + url
    headers = {'Authorization': f'Token {access_token}'}
    params = {'offset': offset, 'limit': limit}
    if purchased is True:
        params['purchased'] = 'true'
    elif purchased is False :
        params['purchased'] = 'false'
    if rented is True:
        params['leased'] = 'true'
    params.update(extra_params)
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_apps_and_extensions: {url}, {resp.status_code}')
    resp = resp.json()
    return resp


def purcharse_arkstore_extension(access_token, extension_id, data):
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/purchase'
    headers = {'Authorization': f'Token {access_token}'}
    params = data
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error purcharse_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def lease_arkstore_extension(access_token, extension_id, data):
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/lease'
    headers = {'Authorization': f'Token {access_token}'}
    params = data
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error lease_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_detail(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_detail: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_detail_by_package(access_token, package):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/extensions/package/{package}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code == 404:
        return
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_detail_by_package: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_price(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/purchase'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_price: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_rent_price(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/lease'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_rent_price: {resp.status_code}')
    resp = resp.json()
    return resp


def order_payment_arkstore_extension(access_token, order_no):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/user/orders/{order_no}/payment'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error order_payment_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def order_payment_status_arkstore_extension(access_token, order_no):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/user/orders/{order_no}/payment_status'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if not(resp.status_code >= 200 and resp.status_code < 300):
        raise Exception(f'Error order_payment_status_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_order_status(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/order/status/extensions/{extension_id}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_order_status: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_rent_status(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/lease/status/extensions/{extension_id}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_rent_status: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_trial_days(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/trial'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_trial_days: {resp.status_code}')
    resp = resp.json()
    return resp


def trial_arkstore_extension(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_id}/trial'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.post(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200 and resp.status_code != 400:
        raise Exception(f'Error trial_arkstore_extension: {resp.status_code}')
    resp = resp.json()
    return resp


def install_arkstore_extension(tenant, token, extension_id):
    saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token)
    access_token = get_arkstore_access_token(tenant, token)
    res = get_arkstore_extension_detail(access_token, extension_id)
    if res['type'] == 'auto_form_fill':
        app = get_arkid_saas_app_detail(tenant, token, extension_id)
        local_app = App.active_objects.filter(tenant=tenant, arkstore_app_id=extension_id).first()
        if not local_app:
            local_app = create_tenant_oidc_app(tenant, app['url'], app['name'], app['description'], app['logo'])
            local_app.arkstore_app_id = res['uuid']
            category_id = res.get('category_id', None)
            if category_id:
                local_app.arkstore_category_id = category_id
                local_app.save()
        local_app.name = app['name']
        local_app.description = app['description']
        local_app.logo = app['logo']

        config = get_app_config()
        frontend_url = config.get_frontend_host(schema=True)
        pname = "com_longgui_auto_form_fill"
        url = f'{frontend_url}/api/v1/{pname}/apps/{local_app.id.hex}/arkid_form_login/'
        local_app.url = url

        local_app.type = 'AutoFormFill'
        local_app.package = 'com.longgui.auto.form.fill'

        local_app.save()
    elif res['type'] == 'extension':
        download_arkstore_extension(tenant, token, extension_id, res)
    elif res['type'] == 'private':
        pass
    else:
        # res['type'] in ('url', 'oidc') or else
        app = get_arkid_saas_app_detail(tenant, token, extension_id)
        url = app['url']
        if '?' in url:
            url = url + f'&tenant_id={saas_tenant_id}'
        else:
            url = url + f'?tenant_id={saas_tenant_id}'
        local_app = create_tenant_oidc_app(tenant, url, app['name'], app['description'], app['logo'])
        category_id = res.get('category_id', None)
        if category_id:
            local_app.arkstore_category_id = category_id
            local_app.save()
        local_app.arkstore_app_id = res['uuid']
        local_app.save()


def download_arkstore_extension(tenant, token, extension_id, extension_detail):
    from arkid import config
    access_token = get_arkstore_access_token(tenant, token)
    ext_package = extension_detail['package'].replace('.', '_')

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
    ext_dir = str(Path(extension_root) / ext_package)
    uninstall_extension(ext_dir)

    # unzip
    import zipfile
    import io
    extract_folder = Path(extension_root)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zip_ref:
        zip_ref.extractall(extract_folder)

    try:
        load_installed_extension(ext_dir, extension_detail)
        logger.info(f'load download extension: {ext_package} scuess')
    except Exception as e:
        logger.exception(f'load download extension: {ext_package} failed: {str(e)}')
        return {'success': 'failed'}

    restart_celery()
    return {'success': 'true'}


def uninstall_extension(ext_dir):
    unload_extension(ext_dir)

    # delete extension folder
    import shutil
    if Path(ext_dir).exists():
        try:
            shutil.rmtree(Path(ext_dir))
        except OSError as e:
            print ("Error remove folder: %s - %s." % (e.filename, e.strerror))
            return {'error': 'delete extension fodler failed'}

    extension = Extension.objects.filter(ext_dir=ext_dir).first()
    if extension:
        extension.delete()


def load_installed_extension(ext_dir, extension_detail):
    ext = import_extension(ext_dir)
    extension, is_create = Extension.objects.update_or_create(
        defaults={
            'type': ext.type,
            'labels': ext.labels,
            'ext_dir': str(ext.ext_dir),
            'name': ext.name,
            'version': ext.version,
            'is_del': False,
        },
        package = ext.package,
    )
    # load_extension_apps([extension])
    category_id = extension_detail.get('category_id', None)
    if category_id:
        extension.category_id = category_id
        extension.save()

    platform_tenant = Tenant.platform_tenant()
    tenant_extension, is_create = TenantExtension.objects.update_or_create(
        defaults={
            'is_rented': True,
        },
        tenant = platform_tenant,
        extension = extension,
    )
    # 插件安装完成需要更新权限开始
    from arkid.core.tasks.celery import dispatch_task
    dispatch_task.delay('update_system_permission')
    # 插件安装完成需要更新权限结束
    # 如果新安装的插件有models需重启django
    extension_models= Path(ext_dir) / 'models.py'
    if extension_models.exists():
        import os
        try:
            print("新安装的插件有models需重启django, 正在重启django server!")
            os.system("supervisorctl restart runserver")
        except Exception as e:
            print("未使用supervisor启动django server, 需手动重启django server!")

    ext.start()


def get_arkstore_private_app_data(tenant, token, app_id):
    access_token = get_arkstore_access_token(tenant, token)
    url = settings.ARKSTOER_URL + f'/api/v1/arkstore/saas_apps/{app_id}/download'
    headers = {'Authorization': f'Token {access_token}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 402:
        resp = resp.json()
        raise Exception(f"error: download failed, msg: {resp.get('msg')}")
    if resp.status_code != 200:
        raise Exception('error: download failed')

    resp = resp.json()
    return resp


def install_arkstore_private_app(tenant, token, app_id, values_data=""):
    data = get_arkstore_private_app_data(tenant, token, app_id)
    download_url = data["download_url"]

    saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token)
    access_token = get_arkstore_access_token(tenant, token)
    res = get_arkstore_extension_detail(access_token, app_id)
    app_name = f"{tenant.id.hex[-8:]}-{res['name']}"[:63]
    k8s_url = settings.K8S_INSTALL_APP_URL + '/crd/chart/' + app_name

    data = {
        "chart": download_url,
        "targetNamespace": app_name,
        "valuesContent": values_data,
    }
    try:
        resp = requests.post(k8s_url, json=data, timeout=30)
        if resp.status_code != 200:
            logger.error(f'Install app to k8s failed: {resp.status_code}')
            return {'code': resp.status_code, 'message': resp.content.decode()}
        resp = resp.json()
        if resp['code'] != 0:
            logger.error(f"Install app to k8s failed: {resp['message']}")
        return resp
    except Exception as e:
        logger.error(f"Install app to k8s failed: {e}")
        return {'code': -1, 'message': str(e)}


def check_private_app_install_status(app_name):
    k8s_url = settings.K8S_INSTALL_APP_URL + '/ahc/crdjob/' + app_name

    try:
        resp = requests.get(k8s_url, timeout=15)
        if resp.status_code != 200:
            logger.error(f'Install app to k8s failed: {resp.status_code}')
            return {'code': resp.status_code, 'message': resp.content.decode()}
        resp = resp.json()
        if resp['code'] != 0:
            logger.error(f"Install app to k8s failed: {resp['message']}")
        return resp
    except Exception as e:
        logger.error(f"Install app to k8s failed: {e}")
        return {'code': -1, 'message': str(e)}


def get_bind_arkstore_agent(access_token):
    order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(order_url, json=params, headers=headers)
    if resp.status_code == 204:
        return {}
    if resp.status_code != 200:
        raise Exception(f'Error get_bind_arkstore_agent: {resp.status_code}')
    resp = resp.json()
    return resp


def bind_arkstore_agent(access_token, tenant_uuid):
    order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'tenant_uuid': tenant_uuid
    }
    resp = requests.post(order_url, json=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
    resp = resp.json()
    return resp


# def change_arkstore_agent(access_token, tenant_slug):
#     order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
#     headers = {'Authorization': f'Token {access_token}'}
#     params = {
#         'tenant_slug': tenant_slug
#     }
#     resp = requests.put(order_url, json=params, headers=headers)
#     if resp.status_code != 200:
#         raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
#     resp = resp.json()
#     return resp


# def unbind_arkstore_agent(access_token):
#     order_url = settings.ARKSTOER_URL + '/api/v1/bind_agent'
#     headers = {'Authorization': f'Token {access_token}'}
#     params = {}
#     resp = requests.delete(order_url, json=params, headers=headers)
#     if resp.status_code != 200:
#         raise Exception(f'Error bind_arkstore_agent: {resp.status_code}')
#     resp = resp.json()
#     return resp


def create_tenant_oidc_app(tenant, url, name, description='', logo=''):
    app, created = App.objects.update_or_create(
            tenant=tenant,
            name=name,
            url=url,
            defaults={"description": description, "logo": logo, 'is_del': False, 'is_active': True}
        )

    if app.entry_permission is None:
        from arkid.core.models import SystemPermission
        from arkid.core.perm.permission_data import PermissionData
        permission = SystemPermission()
        permission.name = app.name
        permission.code = 'entry_{}'.format(uuid.uuid4())
        permission.tenant = tenant
        permission.category = 'entry'
        permission.is_system = True
        permission.save()
        app.entry_permission = permission
        app.save()
        permissiondata = PermissionData()
        permissiondata.update_arkid_all_user_permission(str(tenant.id))
    return app


@transaction.atomic()
def create_tenant_app(tenant, saas_app):
    # from arkid.core.event import Event, register_event, dispatch_event
    # from arkid.core.event import(
    #     CREATE_APP_CONFIG, UPDATE_APP_CONFIG, DELETE_APP,
    #     CREATE_APP_DONE, SET_APP_OPENAPI_VERSION,
    # )
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


def get_arkstore_app_detail(access_token, app_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps/{app_id}/download'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_app_detail: {resp.status_code}')
    resp = resp.json()
    return resp

    
def get_arkid_saas_app_detail(tenant, token, extension_id):
    saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token)
    arkid_saas_app_url = settings.ARKID_SAAS_URL + f'/api/v1/com_longgui_arkidsaas/tenant/{saas_tenant_id}/arkid/saas/app/{extension_id}/'
    headers = {'Authorization': f'Token {saas_token}'}
    params = {}
    resp = requests.get(arkid_saas_app_url, params=params, headers=headers)

    # saas token 失效
    if resp.status_code == 401:
        saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token, use_cache=False)
        headers = {'Authorization': f'Token {saas_token}'}
        resp = requests.get(arkid_saas_app_url, params=params, headers=headers)

    if resp.status_code != 200:
        raise Exception(f'Error get_arkid_saas_app_detail: {resp.status_code}')
    resp = resp.json()
    return resp


def check_arkstore_app_purchased(tenant, token, app):
    access_token = get_arkstore_access_token_with_saas_token(tenant.slug, tenant.id, token)
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps/saas_app_order/{app.id.hex}'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(order_url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise Exception(f'Error check_arkstore_app_purchased: {resp.status_code}')
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


def check_arkstore_purcahsed_extension_expired(tenant, token, package):
    if settings.IS_CENTRAL_ARKID:
        return True

    access_token = get_arkstore_access_token(tenant, token)
    ext_info = get_arkstore_extension_detail_by_package(access_token, package)
    if ext_info is None:
        return True
    extension_uuid = ext_info['uuid']

    price_info = get_arkstore_extension_price(access_token, extension_uuid)
    prices = price_info.get('prices')
    if not prices:
        return True
    for price in prices:
        if price.get('sale_price') == 0:
            return True

    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_uuid}/purchased'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(order_url, params=params, headers=headers, timeout=10)
    if not(resp.status_code >= 200 and resp.status_code < 300):
        print(f'Error check_arkstore_purcahsed_extension_expired: {resp.status_code}')
        return True
    resp = resp.json()
    return check_time_and_user_valid(resp.get('purchase_records') or [], tenant)


def check_arkstore_rented_extension_expired(tenant, token, package):
    if settings.IS_CENTRAL_ARKID:
        return True

    access_token = get_arkstore_access_token(tenant, token)
    ext_info = get_arkstore_extension_detail_by_package(access_token, package)
    if ext_info is None:
        return True
    extension_uuid = ext_info['uuid']
    order_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_uuid}/leased'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(order_url, params=params, headers=headers, timeout=10)
    if not(resp.status_code >= 200 and resp.status_code < 300):
        print(f'Error check_arkstore_rented_extension_expired: {resp.status_code}')
        return True
    resp = resp.json()
    return check_time_and_user_valid(resp.get('lease_records') or [], tenant)


def check_time_and_user_valid(data, tenant):
    max_users_sum = 0
    users_count = len(User.active_objects.filter(tenant=tenant).all())
    for record in data:
        if record.get("use_end_time"):
            expire_time = parse_datetime(record["use_end_time"])
            # expire_time = timezone.make_aware(exp_dt, timezone.get_default_timezone())
            now = timezone.localtime()
            if now > expire_time:
                continue
        if record.get("max_users"):
            if users_count > record["max_users"]:
                max_users_sum += record["max_users"]
            else:
                return True
        else:
            return True
    if users_count > max_users_sum:
        return False
    else:
        return True


# def get_arkstore_extensions_rented(access_token, offset=0, limit=10):
#     url = '/api/v1/arkstore/extensions/leased'
#     arkstore_extensions_url = settings.ARKSTOER_URL + url
#     headers = {'Authorization': f'Token {access_token}'}
#     # params = {'offset': offset, 'limit': limit}
#     params = {'leased': 'true'}
#     resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
#     if resp.status_code != 200:
#         raise Exception(f'Error get_arkstore_apps_and_extensions: {resp.status_code}')
#     resp = resp.json()
#     return resp


# def get_arkstore_extensions_purchased(access_token, offset=0, limit=10):
#     url = '/api/v1/arkstore/extensions/purchased'
#     arkstore_extensions_url = settings.ARKSTOER_URL + url
#     headers = {'Authorization': f'Token {access_token}'}
#     # params = {'offset': offset, 'limit': limit}
#     params = {'purchased': 'true'}
#     resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
#     if resp.status_code != 200:
#         raise Exception(f'Error get_arkstore_apps_and_extensions: {resp.status_code}')
#     resp = resp.json()
#     return resp


def get_arkstore_extension_markdown(access_token, extension_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/extensions/{extension_id}/markdown'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_markdown: {resp.status_code}')
    resp = resp.json()
    return resp


def get_arkstore_extension_history_by_package(access_token, package):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/extensions/package/{package}/history'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_extension_history_by_package: {resp.status_code}')
    resp = resp.json()
    return resp


def click_arkstore_app(access_token, arkstore_app_id):
    arkstore_extensions_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/apps/{arkstore_app_id}/click'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Error click_arkstore_app: {resp.status_code}')
    resp = resp.json()
    return resp

def get_app_config_from_arkstore(request, arkstore_app_id):
    token = request.user.auth_token
    tenant = request.tenant
    access_token = get_arkstore_access_token(tenant, token)
    res = get_arkstore_extension_detail(access_token, arkstore_app_id)
    if res['type'] == 'auto_form_fill':
        app = get_arkid_saas_app_detail(tenant, token, arkstore_app_id)
        return app.get('config', {}).get('config', {})
    return {}


def get_admin_user_token():
    from django.core.cache import cache

    key = "ADMIN_USER_TOKEN"
    value = refresh_admin_uesr_token
    timeout = 60*30
    token = cache.get_or_set(key, value, timeout=timeout)
    return token


def refresh_admin_uesr_token():
    from arkid.core.token import refresh_token
    platform_tenant = Tenant.platform_tenant()
    admin_user = User.objects.filter(
        username='admin', tenant=platform_tenant
    ).first()
    token = refresh_token(admin_user)
    return token
