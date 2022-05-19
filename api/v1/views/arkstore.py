from django.views import View
from django.http import JsonResponse
from collections import OrderedDict
from arkid.core.models import Tenant
from arkid.core.error import ErrorCode
from arkid.common.arkstore import (
    get_arkstore_access_token,
    purcharse_arkstore_extension,
    install_arkstore_extension,
    bind_arkstore_agent,
    get_arkstore_apps_and_extensions,
    get_arkid_saas_app_detail,
)
from arkid.core.api import api
from typing import List
from ninja import Schema
from ninja.pagination import paginate


class ArkstoreExtensionSchemaOut(Schema):
    name: str
    id: str


class BindAgentSchemaIn(Schema):
    tenant_slug: str


@api.get("/tenant/{tenant_id}/arkstore/", tags=['arkstore'], response=List[ArkstoreExtensionSchemaOut])
@paginate
def get_arkstore_extensions(request, tenant_id: str):
    page = request.GET.get('page')
    page_size = request.GET.get('page_size')
    purchased = request.GET.get('purchased')
    token = request.user.auth_token
    tenant = request.tenant
    access_token = get_arkstore_access_token(tenant, token.token)
    # arkstore use offset and limit
    if page and page_size:
        limit = int(page_size)
        offset = (int(page)-1) * int(page_size)
        saas_extensions_data = get_arkstore_apps_and_extensions(access_token, purchased, offset, limit)
    else:
        saas_extensions_data = get_arkstore_apps_and_extensions(access_token, purchased)
    saas_extensions_data = saas_extensions_data['items']
    saas_extensions = []
    for extension_data in saas_extensions_data:
        extension = OrderedDict()
        extension['name'] = extension_data['name']
        extension['description'] = extension_data['description']
        extension['version'] = extension_data['version']
        extension['id'] = extension_data['uuid']
        extension['logo'] = extension_data['logo']
        extension['maintainer'] = extension_data['author']
        # extension['purchased'] = '已购买' if extension_data['purchased'] == True else '未购买'
        extension['purchased'] = extension_data['purchased']
        if extension_data['upgrade']:
            extension['button'] = '升级'
        elif extension['purchased']:
            extension['button'] = '安装'
        else:
            extension['button'] = '购买'
        extension['tags'] = ''
        extension['type'] = extension_data['type']
        extension['scope'] = ''
        extension['homepage'] = ''
        saas_extensions.append(extension)

    return saas_extensions


@api.get("/tenant/{tenant_id}/arkstore/order/{extension_id}/", tags=['arkstore'])
def order_arkstore_extension(request, tenant_id: str, extension_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = purcharse_arkstore_extension(access_token, extension_id)
    return JsonResponse(resp)


@api.get("/tenant/{tenant_id}/arkstore/install/{extension_id}/", tags=['arkstore'])
def download_arkstore_extension(request, tenant_id: str, extension_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = install_arkstore_extension(tenant, token, extension_id)
    result = {'error': ErrorCode.OK.value}
    return JsonResponse(result)


@api.get("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def get_arkstore_bind_agent(request, tenant_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_bind_arkstore_agent(access_token)
    return JsonResponse(resp)


@api.post("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def create_arkstore_bind_agent(request, tenant_id: str, data: BindAgentSchemaIn):
    tenant_slug = data.tenant_slug
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = bind_arkstore_agent(access_token, tenant_slug)
    return JsonResponse(resp)


@api.delete("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def delete_arkstore_bind_agent(request, tenant_id: str):
    tenant_slug = data.tenant_slug
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = change_arkstore_agent(access_token, tenant_slug)
    return JsonResponse(resp)


@api.put("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def update_arkstore_bind_agent(request, tenant_id: str, data: BindAgentSchemaIn):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = unbind_arkstore_agent(access_token)
    return JsonResponse(resp)


@api.get("/tenant/{tenant_id}/arkstore/auto_fill_form/{app_id}/", tags=['arkstore'])
def get_arkstore_app(request, tenant_id: str, app_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = get_arkid_saas_app_detail(tenant, token, app_id)
    return JsonResponse(result)

