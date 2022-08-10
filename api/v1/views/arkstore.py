from django.http import JsonResponse
from collections import OrderedDict
from arkid.core.constants import *
from arkid.core.models import Platform, Tenant, App
from arkid.core.error import ErrorCode, ErrorDict
from arkid.common.arkstore import (
    check_arkstore_purcahsed_extension_expired,
    check_arkstore_rented_extension_expired,
    get_arkstore_access_token,
    get_arkstore_extension_detail_by_package,
    purcharse_arkstore_extension,
    lease_arkstore_extension,
    install_arkstore_extension,
    get_arkstore_extensions,
    get_arkstore_extension_detail,
    get_arkstore_extension_price,
    get_arkstore_extension_rent_price,
    order_payment_arkstore_extension,
    order_payment_status_arkstore_extension,
    get_arkstore_extension_order_status,
    get_arkstore_extension_rent_status,
    get_arkstore_extension_trial_days,
    trial_arkstore_extension,
    get_arkid_saas_app_detail,
    get_bind_arkstore_agent,
    bind_arkstore_agent,
    # change_arkstore_agent,
    # unbind_arkstore_agent,
    get_arkstore_extension_markdown,
    get_arkstore_extension_history_by_package,
)
from arkid.common.bind_saas import get_bind_info
from arkid.core.api import api, operation
from datetime import datetime
from typing import List, Optional
from ninja import Schema, Query
import enum
from pydantic import Field
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.extension.models import Extension, TenantExtension
from arkid.core.translation import gettext_default as _
from pydantic import condecimal, conint
from arkid.core.schema import ResponseSchema



def get_arkstore_list(request, purchased, type, rented=False, all=False, extra_params={}):
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    token = request.user.auth_token
    tenant = request.tenant
    access_token = get_arkstore_access_token(tenant, token.token)
    # arkstore use offset and limit
    if page and page_size:
        limit = int(page_size)
        offset = (int(page)-1) * int(page_size)
    if all:
        limit = 1000000
        offset = 0
    saas_extensions_data = get_arkstore_extensions(access_token, purchased, rented, type, offset, limit, extra_params)
    saas_extensions_data = saas_extensions_data['items']
    return saas_extensions_data


class ArkstoreItemSchemaOut(Schema):
    uuid: str = Field(hidden=True)
    name: str = Field(readonly=True)
    package: Optional[str] = Field(readonly=True)
    version: str = Field(readonly=True, title=_('Version', '版本'))
    author: str = Field(readonly=True, title=_('Author', '作者'))
    logo: str = Field(readonly=True, default="")
    description: str = Field(readonly=True)
    categories: str = Field(readonly=True)
    labels: str = Field(readonly=True)
    homepage: str = Field(readonly=True, title=_('Homepage', '官方网站'))
    # "status",
    # "created",
    # "type",
    # button: str


class UserExtensionOut(Schema):
    order_type: str
    price_type: str
    use_begin_time: datetime
    use_end_time: datetime
    max_users: int


class OnShelveExtensionPurchaseOut(ArkstoreItemSchemaOut):
    # purchased: bool = False
    # purchase_records: List[UserExtensionOut] = Field(
    #     default=[], title=_("Purchase Records", "购买记录")
    # )
    purchase_state: Optional[str] = Field(
        title=_('Purchase State', '购买状态')
    )
    purchase_useful_life: Optional[List[str]] = Field(
        title=_('Purchase Useful Life', '有效期')
    )


class OrderStatusSchema(Schema):
    purchased: bool


class BindAgentSchema(Schema):
    tenant_uuid: Optional[str] = Field(
        title=_('Agent Identifier', '代理商标识')
    )


class BindAgentSchemaOut(ResponseSchema):
    data: Optional[BindAgentSchema]


class PriceSchema(Schema):
    uuid: str = Field(hidden=True)
    type: str = Field(title=_('Payment Type', '付费方式'))
    days: int = Field(title=_('Days', '天数'))
    users: int = Field(title=_('Users', '人数'))
    standard_price: str =Field(underline=True, title=_('Standard Price', '市场指导价'))
    sale_price: str =Field(title=_('Agent Sale Price', '代理价格'))


class ExtensionOrderOut(Schema):
    prices: List[PriceSchema] = Field(
        hidden=True, title=_("Extension Prices", "插件价格")
    )


class OrderSchemaIn(Schema):
    users_copies: int
    days_copies: int
    price_uuid: str


class OrderSchema(Schema):
    order_no: str = Field(format='qrcode')


class OrderSchemaOut(ResponseSchema):
    data: Optional[OrderSchema]


class SetCopies(Schema):
    days_copies: conint(ge=1) = Field(default=1, title=_('Days Copies', '份数(天)'))
    users_copies: conint(ge=1) = Field(default=1, title=_('Users Copies', '份数(人)'))


class OrderPaymentUrlOut(Schema):
    code_url: str = Field(title="微信支付二维码", format="qrcode")

class OrderPaymentOut(ResponseSchema):
    data: OrderPaymentUrlOut


class TrialDays(Schema):
    trial_period: int = Field(readonly=True, title=_('Trial Days',"试用期(天)"))


class TrialDaysOut(ResponseSchema):
    data: TrialDays


class Payer(Schema):
    openid: str


class TradeState(str, enum.Enum):
    SUCCESS = "SUCCESS"
    REFUND = "REFUND"
    NOTPAY = "NOTPAY"
    CLOSED = "CLOSED"
    REVOKED = "REVOKED"
    USERPAYING = "USERPAYING"
    PAYERROR = "PAYERROR"


class Amount(Schema):
    total: Optional[int]
    payer_total: Optional[int]
    currency: Optional[str]
    payer_currency: Optional[str]


class PaymentStatus(Schema):
    appid: str
    mchid: str
    out_trade_no: str
    transaction_id: str = Field(default='')
    trade_type: str = Field(default='')
    trade_state: TradeState
    trade_state_desc: str
    bank_type: str = Field(default='')
    attach: str = Field(default='')
    success_time: str = Field(default='')
    payer: Payer = Field(default=None)
    amount: Amount


class ArkstoreExtensionQueryIn(Schema):
    name__contains:str = Field(
        default="",
        title=_("插件名")
    )
    package__contains:str = Field(
        default="",
        title=_("插件包名")
    )
    labels__contains:str = Field(
        default="",
        title=_("插件标签")
    )


class ArkstoreAppQueryIn(Schema):
    name__contains:str = Field(
        default="",
        title=_("应用名")
    )
    labels__contains:str = Field(
        default="",
        title=_("应用标签")
    )


@api.get("/tenant/{tenant_id}/arkstore/extensions/", tags=['方舟商店'], response=List[OnShelveExtensionPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_extensions(request, tenant_id: str, query_data: ArkstoreExtensionQueryIn=Query(...)):
    query_data = query_data.dict()
    return get_arkstore_list(request, None, 'extension', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/apps/", tags=['方舟商店'], response=List[ArkstoreItemSchemaOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_apps(request, tenant_id: str, query_data: ArkstoreAppQueryIn=Query(...)):
    query_data = query_data.dict()
    return get_arkstore_list(request, None, 'app', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/purchased/extensions/", tags=['方舟商店'], response=List[OnShelveExtensionPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_purchased_extensions(request, tenant_id: str):
    return get_arkstore_list(request, True, 'extension')


@api.get("/tenant/{tenant_id}/arkstore/purchased/apps/", tags=['方舟商店'], response=List[ArkstoreItemSchemaOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_purchased_apps(request, tenant_id: str):
    arkstore_apps = get_arkstore_list(request, None, 'app', all=True)
    installed_apps = App.active_objects.filter(tenant_id=tenant_id, arkstore_app_id__isnull=False)
    installed_app_ids = set(str(app.arkstore_app_id) for app in installed_apps)
    return [app for app in arkstore_apps if app['uuid'] in installed_app_ids]


@api.get("/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/", tags=['方舟商店'],
         response=List[PriceSchema])
@operation(List[PriceSchema], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_order_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extension_price(access_token, uuid)
    return resp['prices']


@api.post("/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/", tags=['方舟商店'], 
          response=OrderSchema)
@operation(OrderSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_order_arkstore_extension(request, tenant_id: str, uuid: str, data: OrderSchemaIn):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = purcharse_arkstore_extension(access_token, uuid, data.dict())
    return resp


@api.post("/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/set_copies/", tags=['方舟商店'],
          response=SetCopies)
@operation(SetCopies, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def set_copies_order_arkstore_extension(request, tenant_id: str, uuid: str, data: SetCopies):
    return


@api.get("/tenant/{tenant_id}/arkstore/order/{order_no}/payment/", tags=['方舟商店'], response=OrderPaymentOut)
@operation(OrderPaymentOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_order_payment_arkstore_extension(request, tenant_id: str, order_no: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = order_payment_arkstore_extension(access_token, order_no)
    return {'data': resp}


@api.get("/tenant/{tenant_id}/arkstore/purchase/order/{order_no}/payment_status/", tags=['方舟商店'],
    response={
        200: PaymentStatus,
        202: ResponseSchema,
    })
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_order_payment_status_arkstore_extension(request, tenant_id: str, order_no: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = order_payment_status_arkstore_extension(access_token, order_no)
    if resp.get('code') == '0' and not resp.get('appid'):
        return 202, {'data': resp}
    else:
        return 200, resp


@api.get("/tenant/{tenant_id}/arkstore/rent/order/{order_no}/payment_status/extensions/{package}/", tags=['方舟商店'], 
    response={
        200: PaymentStatus,
        202: ResponseSchema,
    })
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_order_payment_status_arkstore_extension_rent(request, tenant_id: str, order_no: str, package: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = order_payment_status_arkstore_extension(access_token, order_no)
    if check_arkstore_rented_extension_expired(tenant, token, package):
        extension = Extension.valid_objects.filter(package=package).first()
        tenant_extension, created = TenantExtension.objects.update_or_create(
            tenant_id=tenant_id,
            extension=extension,
            defaults={"is_rented": True}
        )
    if resp.get('code') == '0' and not resp.get('appid'):
        return 202, {'data': resp}
    else:
        return 200, resp


@api.get("/tenant/{tenant_id}/arkstore/order/status/extensions/{uuid}/", tags=['方舟商店'], response=OrderStatusSchema)
@operation(OrderStatusSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def order_status_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extension_order_status(access_token, uuid)
    return resp


@api.get("/tenant/{tenant_id}/arkstore/rent/extensions/{package}/", tags=['方舟商店'], response=List[PriceSchema])
@operation(List[PriceSchema], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_rent_arkstore_extension(request, tenant_id: str, package: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    ext_info = get_arkstore_extension_detail_by_package(access_token, package)
    if ext_info is None:
        extension = Extension.valid_objects.filter(package=package).first()
        tenant_extension, created = TenantExtension.objects.update_or_create(
            tenant_id=tenant_id,
            extension=extension,
            defaults={"is_rented": True}
        )
        return ErrorDict(ErrorCode.RENT_EXTENSION_SUCCESS)
    resp = get_arkstore_extension_rent_price(access_token, ext_info['uuid'])
    return resp['prices']


@api.post("/tenant/{tenant_id}/arkstore/rent/extensions/{package}/", tags=['方舟商店'], response=OrderSchema)
@operation(OrderSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_rent_order_arkstore_extension(request, tenant_id: str, package: str, data: OrderSchemaIn):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    ext_info = get_arkstore_extension_detail_by_package(access_token, package)
    if ext_info is None:
        return {}
    platform_tenant = Tenant.platform_tenant()
    resp = get_bind_info(platform_tenant.id.hex)
    agent_uuid = resp.get('saas_tenant_id')
    rent_data = data.dict()
    rent_data['agent_uuid'] = agent_uuid
    resp = lease_arkstore_extension(access_token, ext_info['uuid'], rent_data)
    return resp


@api.post("/tenant/{tenant_id}/arkstore/rent/extensions/{uuid}/", tags=['方舟商店'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def rent_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    # platform_tenant = Tenant.objects.filter(slug='').first()
    # saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(platform_tenant, token)
    access_token = get_arkstore_access_token(tenant, token)
    # bind_arkstore_agent(access_token, saas_tenant_slug)
    resp = lease_arkstore_extension(access_token, uuid)
    return resp


@api.post("/tenant/{tenant_id}/arkstore/rent/status/extensions/{uuid}/", tags=['方舟商店'], response=OrderStatusSchema)
@operation(OrderStatusSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def rent_status_arkstore_extension(request, tenant_id: str, uuid: str):
    if Platform.get_config().is_need_rent:
        token = request.user.auth_token
        tenant = Tenant.objects.get(id=tenant_id)
        access_token = get_arkstore_access_token(tenant, token)
        resp = get_arkstore_extension_rent_status(access_token, uuid)
        if resp.get('error'):
            return resp
    
    tenant_extension, created = TenantExtension.objects.update_or_create(
        tenant_id=tenant_id,
        extension_id=uuid,
        defaults={"is_rented": True}
    )
    return {'purchased':True}


@api.get("/tenant/{tenant_id}/arkstore/trial/extensions/{uuid}/", tags=['方舟商店'], response=TrialDaysOut)
@operation(TrialDaysOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_order_arkstore_extension_trial(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extension_trial_days(access_token, uuid)
    return {'data': resp}


@api.post("/tenant/{tenant_id}/arkstore/trial/extensions/{uuid}/", tags=['方舟商店'], response=OrderSchemaOut)
@operation(OrderSchemaOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_order_arkstore_extension_trial(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = trial_arkstore_extension(access_token, uuid)
    if resp.get('code') == '10003':
        return ErrorDict(ErrorCode.TRIAL_EXTENSION_TWICE)
    return {'data': resp}


@api.post("/tenant/{tenant_id}/arkstore/install/{uuid}/", tags=['方舟商店'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def download_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = install_arkstore_extension(tenant, token, uuid)
    resp = {'error': ErrorCode.OK.value, 'data': {}}
    return resp


@api.post("/tenant/{tenant_id}/arkstore/update/{package}/", tags=['方舟商店'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_arkstore_extension(request, tenant_id: str, package: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    ext_info = get_arkstore_extension_detail_by_package(access_token, package)
    if ext_info is None:
        return ErrorDict(ErrorCode.UPDATE_EXTENSION_SUCCESS)
    result = install_arkstore_extension(tenant, token, ext_info['uuid'])
    resp = {'error': ErrorCode.OK.value, 'data': {}}
    return resp


@api.get("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['方舟商店'], response=BindAgentSchemaOut)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_arkstore_bind_agent(request, tenant_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_bind_arkstore_agent(access_token)
    return {'data': resp}


@api.post("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['方舟商店'], response=BindAgentSchemaOut)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_arkstore_bind_agent(request, tenant_id: str, data: BindAgentSchema):
    tenant_uuid = data.tenant_uuid
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_bind_arkstore_agent(access_token)
    if resp.get('tenant_uuid'):
        return ErrorDict(ErrorCode.AGENT_BIND_CAN_NOT_CHANGE)
    resp = bind_arkstore_agent(access_token, tenant_uuid)
    return {'data': resp}


# @api.delete("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['方舟商店'])
# @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
# def delete_arkstore_bind_agent(request, tenant_id: str):
#     token = request.user.auth_token
#     tenant = Tenant.objects.get(id=tenant_id)
#     access_token = get_arkstore_access_token(tenant, token)
#     resp = unbind_arkstore_agent(access_token)
#     return resp


# @api.put("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['方舟商店'])
# @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
# def update_arkstore_bind_agent(request, tenant_id: str, data: BindAgentSchema):
#     tenant_slug = data.tenant_slug
#     token = request.user.auth_token
#     tenant = Tenant.objects.get(id=tenant_id)
#     access_token = get_arkstore_access_token(tenant, token)
#     resp = change_arkstore_agent(access_token, tenant_slug)
#     return resp


@api.get("/tenant/{tenant_id}/arkstore/auto_fill_form/{uuid}/", tags=['方舟商店'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_arkstore_app(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    resp = get_arkid_saas_app_detail(tenant, token, uuid)
    return resp


class ExtensionMarkDownOut(ResponseSchema):
    data:dict = Field(format='markdown',readonly=True)


@api.get("/tenant/{tenant_id}/arkstore/extensions/{uuid}/markdown/", tags=['方舟商店'],
         response=ExtensionMarkDownOut)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_markdown_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extension_markdown(access_token, uuid)
    return resp


class ArkstoreItemHisotryOut(Schema):
    uuid: str = Field(hidden=True)
    version: str = Field(readonly=True, title=_('Version', '版本'))


@api.get("/tenant/{tenant_id}/arkstore/extensions/{package}/history/", tags=['方舟商店'], response=List[ArkstoreItemHisotryOut])
@operation(List[ArkstoreItemHisotryOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_arkstore_extension_history(request, tenant_id: str, package: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extension_history_by_package(access_token, package)
    return resp['items']
