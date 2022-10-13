import os
import requests
from arkid.config import get_app_config
from arkid.core.models import Tenant
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.models import Application
from arkid.common.arkstore import create_tenant_oidc_app
from arkid.core.models import Platform
from arkid.core.event import listen_event, SET_FRONTEND_URL


def get_bind_info(tenant_id):
    bind_saas_url = settings.ARKID_SAAS_URL + '/api/v1/arkid/saas/bind'
    params = {'local_tenant_id': tenant_id}
    resp = requests.get(bind_saas_url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_bind_info: {resp.status_code}')
    resp = resp.json()
    if resp.get('saas_tenant_id'):
        tenant = Tenant.objects.get(id=tenant_id)
        create_arkidstore_login_app(tenant, resp['saas_tenant_id'])
        create_arkid_saas_login_app(tenant, resp['saas_tenant_id'], resp.get('saas_login_url'))
    return resp


def create_oidc_app(tenant):
    redirect_uris = ''
    defaults = {
        'client_type': 'public',
        'redirect_uris': redirect_uris,
        'authorization_grant_type': 'implicit',
        'skip_authorization': True,
        'algorithm': 'HS256',
    }

    app, created = Application.objects.update_or_create(
        uuid = tenant.id,
        name = 'arkid_saas',
        defaults=defaults,
    )
    return app


def create_saas_binding(tenant, data, app):
    bind_saas_url = settings.ARKID_SAAS_URL + '/api/v1/arkid/saas/bind'
    host = get_app_config().get_host()
    # jwks_url = f"{host}/api/v1/tenant/{tenant.id.hex}/.well-known/jwks.json"
    # resp = requests.get(jwks_url)
    # if resp.status_code != 200:
    #     raise Exception(f'Error get_jwks: {resp.status_code}')
    # jwks = resp.text
    jwks = ''
    params = {
        'local_tenant_id': str(tenant.id),
        'local_tenant_slug': tenant.slug,
        'company_name': data['company_name'],
        'contact_person': data['contact_person'],
        'email': data['email'],
        'mobile': data['mobile'],
        'client_id': app.client_id,
        'client_secret': app.client_secret,
        'local_host': host,
        'saas_tenant_slug': data['saas_tenant_slug'],
        'jwks': jwks,
    }
    resp = requests.post(bind_saas_url, json=params)
    if resp.status_code != 200:
        raise Exception(f'Error create_saas_binding: {resp.status_code}')
    resp = resp.json()
    return resp


def update_saas_binding(tenant, data):
    bind_saas_url = settings.ARKID_SAAS_URL + '/api/v1/arkid/saas/bind'
    host = get_app_config().get_host()
    params = {
        'local_tenant_id': str(tenant.id),
        'company_name': data['company_name'],
        'contact_person': data['contact_person'],
        'email': data['email'],
        'mobile': data['mobile'],
    }
    resp = requests.patch(bind_saas_url, json=params)
    if resp.status_code != 200:
        raise Exception(f'Error update_saas_binding: {resp.status_code}')
    resp = resp.json()
    return resp


def set_saas_bind_slug(tenant, data):
    bind_saas_url = settings.ARKID_SAAS_URL + '/api/v1/arkid/saas/bind/slug'
    params = {
        'local_tenant_id': str(tenant.id),
        'saas_tenant_slug': data['saas_tenant_slug'],
    }
    resp = requests.post(bind_saas_url, json=params)
    if resp.status_code != 200:
        raise Exception(f'Error update_saas_binding: {resp.status_code}')
    resp = resp.json()
    return resp


def create_arkidstore_login_app(tenant, saas_tenant_id):
    from arkid.core.models import App
    url = f"{settings.ARKSTOER_URL}/api/v1/login?tenant_id={saas_tenant_id}"
    app = App.objects.filter(tenant=tenant, name="ArkStore", url=url)
    if app:
        app.delete()
    create_tenant_oidc_app(tenant, url, '开发与代理', '开发商与代理商的管理后台',
        'https://s1.ax1x.com/2022/07/04/jJrVxg.png')


def create_arkid_saas_login_app(tenant, saas_tenant_id, saas_login_url=None):
    from arkid.core.models import App
    url = saas_login_url or f"{settings.ARKID_SAAS_URL}/login?tenant_id={saas_tenant_id}"
    app = App.objects.filter(tenant=tenant, name="Central ArkID", url=url)
    if app:
        app.delete()
    # create_tenant_oidc_app(tenant, url, 'Central ArkID', '中心ArkID', 
    #     'https://s1.ax1x.com/2022/07/04/jJDh2F.png')


def bind_saas(tenant_id, data=None):
    # 正式环境等待frontend_url设置完成后才开始绑定中心arkid
    config = Platform.get_config()
    if os.environ.get('K8SORDC') and config.frontend_url is None:
        return {}
    from django.conf import settings
    if settings.IS_CENTRAL_ARKID:
        return {}
    tenant = Tenant.objects.get(id=tenant_id)
    if not data:
        data = {
            'company_name': '',
            'contact_person': '',
            'email': '',
            'mobile': '',
            'saas_tenant_slug': None,
        }
    bind_info = get_bind_info(tenant.id.hex)
    if bind_info.get('saas_tenant_id'):
        # bind_info = update_saas_binding(tenant, data)
        return bind_info
    
    app = create_oidc_app(tenant)

    try:
        resp = create_saas_binding(tenant, data, app)
        if 'error' in resp:
            app.delete()
            return resp
    except Exception as e:
        app.delete()
        data = {'error': str(e)}
        return data

    app.redirect_uris = resp['callback_url']
    app.save()

    data = {
        'saas_tenant_id': resp['saas_tenant_id'],
        'saas_tenant_slug': resp['saas_tenant_slug'],
    }
    create_arkidstore_login_app(tenant, resp['saas_tenant_id'])
    create_arkid_saas_login_app(tenant, resp['saas_tenant_id'], resp.get('saas_login_url'))
    return data


def trigger_bind_saas(event, **kwargs):
    from arkid.core.tasks.celery import dispatch_task
    from django.conf import settings
    if not settings.IS_CENTRAL_ARKID:
        dispatch_task.delay('bind_arkid_saas_all_tenants')

listen_event(SET_FRONTEND_URL, trigger_bind_saas)
