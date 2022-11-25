from django.http import JsonResponse
from collections import OrderedDict
from enum import Enum
from ninja import ModelSchema
from arkid.core.constants import *
from arkid.core.models import Platform, Tenant, App, PrivateApp
from arkid.core.error import ErrorCode, ErrorDict
from arkid.common.arkstore import (
    check_arkstore_purcahsed_extension_expired,
    check_arkstore_rented_extension_expired,
    check_time_and_user_valid,
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
    click_arkstore_app,
    install_arkstore_private_app,
    delete_arkstore_private_app,
    get_arkstore_private_app_data,
)
from arkid.common.bind_saas import get_bind_info
from arkid.core.api import api, operation
from datetime import datetime
from typing import List, Optional, Any
from ninja import Schema, Query
import enum
from pydantic import Field
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination, ArstorePagination, ArstoreExtensionPagination, ArstoreAppPagination
from arkid.extension.models import Extension, TenantExtension, ArkStoreCategory
from arkid.core.translation import gettext_default as _
from pydantic import condecimal, conint
from arkid.core.schema import ResponseSchema
from django.conf import settings
from arkid.core import actions


def get_arkstore_list(request, purchased, type, rented=False, all=False, extra_params={}):
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    token = request.user.auth_token
    tenant = request.tenant
    access_token = get_arkstore_access_token(tenant, token)
    # arkstore use offset and limit
    if page and page_size:
        limit = int(page_size)
        offset = (int(page)-1) * int(page_size)
    if all:
        limit = 1000000
        offset = 0
    saas_extensions_data = get_arkstore_extensions(access_token, purchased, rented, type, offset, limit, extra_params)
    if type != 'category':
        # 分类不需要额外处理
        for ext in saas_extensions_data['items']:
            if 'type' in ext:
                ext['type'] = 'arkstore_' + ext['type']
    return saas_extensions_data


class ITEM_TYPE(str, Enum):
    arkstore_extension =  _("arkstore_extension", "ArkID插件")
    arkstore_oidc =  _("arkstore_oidc", "OIDC应用")
    arkstore_auto_form_fill =  _("arkstore_auto_form_fill", "表单代填应用")
    arkstore_url =  _("arkstore_url", "推广链接")
    arkstore_custom =  _("arkstore_custom", "自定义")
    arkstore_private =  _("arkstore_private", "私有化应用")


class PAYMENT_TYPE(str, Enum):
    in_app =  _("in_app", "应用内付费"),
    in_store =  _("in_store", "商店内付费"),
    custom =  _("custom", "自定义"),


class ArkstoreItemSchemaOut(Schema):
    uuid: str = Field(hidden=True)
    local_uuid: Optional[str] = Field(hidden=True, title=_('Local UUID', '插件本地UUID'))
    arkstore_uuid: Optional[str] = Field(hidden=True, title=_('Arkstore UUID', '插件商店UUID'))
    name: str = Field(readonly=True)
    version: str = Field(readonly=True, title=_('Version', '版本'))
    author: str = Field(readonly=True, title=_('Author', '作者'))
    logo: str = Field(readonly=True, default="")
    description: Optional[str] = Field(readonly=True)
    category: Optional[str] = Field(title=_('Category', '分类'), readonly=True)
    labels: Optional[str] = Field(title=_('Labels', '标签'), readonly=True)
    homepage: str = Field(readonly=True, title=_('Homepage', '官方网站'))


class ArkstoreAppItemSchemaOut(ArkstoreItemSchemaOut):
    type: Optional[ITEM_TYPE] = Field(title=_('Access Type', '接入方式'), readonly=True)
    payment_mode: Optional[PAYMENT_TYPE] = Field(title=_('Payment Mode', '支付方式'), readonly=True)
    can_buy: Optional[bool] = Field(title=_("Can Buy", "允许购买"), default=False, hidden=True)
    can_try: Optional[bool] = Field(title=_("Can Try", "允许试用"), default=False, hidden=True)


class ArkstoreExtensionItemSchemaOut(ArkstoreItemSchemaOut):
    package: Optional[str] = Field(readonly=True)

class ArkstoreCategoryItemSchemaOut(Schema):

    id: str = Field(alias='arkstore_id')
    name: str = Field(alias='arkstore_name', default='')

    # class Config:
    #     model = ArkStoreCategory
    # model_fields = []

class ArkstoreCategoryListSchemaOut(ResponseSchema):
    data: List[ArkstoreCategoryItemSchemaOut]

class UserExtensionOut(Schema):
    order_type: str
    price_type: str
    use_begin_time: datetime
    use_end_time: datetime
    max_users: int


class OnShelveExtensionPurchaseOut(ArkstoreExtensionItemSchemaOut):
    purchase_state: Optional[str] = Field(
        title=_('Purchase State', '购买状态')
    )
    purchase_useful_life: Optional[List[str]] = Field(
        title=_('Purchase Useful Life', '有效期')
    )
    installed: Optional[bool] = Field(title=_("Installed", "已安装"), default=True, hidden=True)
    has_upgrade: Optional[bool] = Field(title=_("Has Upgrade", "有升级"), default=False, hidden=True)
    lease_state: Optional[str] = Field(title=_('Lease State', '租赁状态'))
    lease_useful_life: Optional[List[str]] = Field(title=_('Lease Useful Life', '有效期'))
    is_active: Optional[bool] = Field(
        title='是否启动',
        item_action={
            "path":"/api/v1/extensions/{id}/toggle/",
            "method":actions.FrontActionMethod.POST.value
        }
    )
    is_active_tenant: Optional[bool] = Field(
        title='是否使用',
        item_action={
            "path":"/api/v1/tenant/{tenant_id}/tenant/extensions/{id}/active/",
            "method":actions.FrontActionMethod.POST.value
        }
    )
    is_default_extension: Optional[bool] = Field(title=_("Is Default Extension", "是否系统自带插件"), default=False, hidden=True)


class OnShelveAppPurchaseOut(ArkstoreExtensionItemSchemaOut):
    type: Optional[ITEM_TYPE] = Field(title=_('Access Type', '接入方式'), readonly=True)
    payment_mode: Optional[PAYMENT_TYPE] = Field(title=_('Payment Mode', '支付方式'), readonly=True)
    purchase_state: Optional[str] = Field(
        title=_('Purchase State', '购买状态')
    )
    purchase_useful_life: Optional[List[str]] = Field(
        title=_('Purchase Useful Life', '有效期')
    )
    installed: Optional[bool] = Field(title=_("Installed", "已安装"), default=False, hidden=True)
    has_upgrade: Optional[bool] = Field(title=_("Has Upgrade", "有升级"), default=False, hidden=True)
    private_app_status: Optional[str] = Field(
        title=_('Private App Status', "私有化应用安装状态")
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
    days: str = Field(title=_('Days', '天数'))
    users: str = Field(title=_('Users', '人数'))
    standard_price: str =Field(linethrough=True, title=_('Standard Price', '市场指导价'))
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
    category_id:str = Field(
        default="",
        title=_("应用分类")
    )
    search:str = Field(
        default="",
        title=_("任一字段")
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
    category_id:str = Field(
        default="",
        title=_("应用分类")
    )
    search:str = Field(
        default="",
        title=_("任一字段")
    )


class ArkstoreAllAppQueryIn(ArkstoreAppQueryIn):
    type:str = Field(
        default="",
        title=_("应用类型")
    )

class OnShelveAppPurchaseResponse(ResponseSchema):
    data: OnShelveAppPurchaseOut


@api.get("/tenant/{tenant_id}/arkstore/extensions/", tags=['方舟商店'], response=List[OnShelveExtensionPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
@paginate(ArstoreExtensionPagination)
def list_arkstore_extensions(request, tenant_id: str, query_data: ArkstoreExtensionQueryIn=Query(...)):
    query_data = query_data.dict()
    return get_arkstore_list(request, None, 'extension', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/apps/", tags=['方舟商店'], response=List[ArkstoreAppItemSchemaOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(ArstorePagination)
def list_arkstore_apps(request, tenant_id: str, query_data: ArkstoreAppQueryIn=Query(...)):
    query_data = query_data.dict()
    query_data['type'] = 'app'
    return get_arkstore_list(request, None, 'app', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/private_apps/", tags=['方舟商店'], response=List[ArkstoreAppItemSchemaOut])
@operation(List[ArkstoreItemSchemaOut], roles=[PLATFORM_ADMIN])
@paginate(ArstorePagination)
def list_arkstore_private_apps(request, tenant_id: str, query_data: ArkstoreAppQueryIn=Query(...)):
    query_data = query_data.dict()
    query_data['type'] = 'private_app'
    return get_arkstore_list(request, None, 'app', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/all/apps/", tags=['方舟商店'], response=List[OnShelveAppPurchaseOut])
@operation(List[OnShelveAppPurchaseOut], roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(ArstoreAppPagination)
def list_arkstore_all_apps(request, tenant_id: str, query_data: ArkstoreAllAppQueryIn=Query(...)):
    query_data = query_data.dict()
    query_data['type'] = query_data.pop('type', None) or 'all'
    return get_arkstore_list(request, None, 'app', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/purchased/all/apps/", tags=['方舟商店'], response=List[OnShelveAppPurchaseOut])
@operation(List[OnShelveAppPurchaseOut], roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(ArstoreAppPagination)
def list_arkstore_purchased_all_apps(request, tenant_id: str, query_data: ArkstoreAllAppQueryIn=Query(...)):
    query_data = query_data.dict()
    query_data['type'] = query_data.pop('type', None) or 'all'
    return get_arkstore_list(request, True, 'app', extra_params=query_data)


@api.get("/tenant/{tenant_id}/arkstore/purchased/all/apps/{arkstore_uuid}/", tags=['方舟商店'], response=OnShelveAppPurchaseResponse)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_arkstore_purchased_app(request, tenant_id: str, arkstore_uuid: str):
    token = request.user.auth_token
    tenant = request.tenant
    access_token = get_arkstore_access_token(tenant, token)
    app = get_arkstore_extension_detail(access_token, arkstore_uuid)

    installed_private_app = PrivateApp.active_objects.filter(tenant=tenant, arkstore_app_id=arkstore_uuid).first()
    installed_app = App.active_objects.filter(tenant=tenant, arkstore_app_id=arkstore_uuid).first()

    app.pop('category', None)
    app['arkstore_uuid'] = arkstore_uuid
    if installed_app:
        app['local_uuid'] = str(installed_app.id)
        app['installed'] = True
    elif installed_private_app:
        app['installed'] = True
        app['private_app_status'] = installed_private_app.status

    if 'type' in app:
        app['type'] = 'arkstore_' + app['type']

    return {"data": app}


@api.get("/tenant/{tenant_id}/arkstore/categorys/", tags=['方舟商店'], response=ArkstoreCategoryListSchemaOut)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN,NORMAL_USER])
def list_arkstore_categorys(request, tenant_id: str, parent_id:str = None, type:str = 'app', show_local:int = 0):
    '''
    方舟商店分类列表
    '''

    items = ArkStoreCategory.valid_objects.filter()
    if not items.exists():
        # 如果没有商品分类信息(第一次)
        get_arkstore_category_http()
        items = ArkStoreCategory.valid_objects.filter()
    items = items.filter(arkstore_type=type)
    if parent_id in [None,""]:
        # 未传则获取所有一级分组
        items = items.filter(arkstore_parent_id=None)
    elif parent_id in [0,"0"]:
        # 虚拟节点返回空
        items = []
    else:
        items = items.filter(arkstore_parent_id=parent_id)
    # result = {
    #     "data": [
    #         {
    #             "id": 17,
    #             "name": "化学"
    #         },
    #         {
    #             "id": 26,
    #             "name": "历史"
    #         }
    #     ]
    # }
    # data = result.get('data', [])
    result = []
    if show_local == 1 and parent_id in [None,""]:
        result.append({
            'arkstore_id': -1,
            'arkstore_name': '自建应用' 
        })
        if items:
            ids = []
            for item in items:
                temp_items = []
                item.get_all_child(temp_items)
                if App.valid_objects.filter(arkstore_category_id__in=temp_items).exists():
                    ids.append(item.id)
            if ids:
                items = items.filter(id__in=ids)
                result.extend(list(items.order_by('arkstore_id')))
            else:
                items = []
    else:
        if items:
            result.extend(list(items.order_by('arkstore_id')))
    return {'data': result}


def get_arkstore_category_http():
    '''
    同步arkstore分类(只有没分类的时候才会爬一次)
    '''
    from django.conf import settings
    import requests
    import logging
    url = '/api/v1/arkstore/all_categories'
    resp = requests.get(settings.ARKSTOER_URL + url)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_apps_and_extensions: {url}, {resp.status_code}')
    resp = resp.json()
    data = resp.get('data', [])
    all_arkstore_categorys = ArkStoreCategory.valid_objects.all()
    all_arkstore_category_ids = []
    for arkstore_category_item in all_arkstore_categorys:
        all_arkstore_category_ids.append(str(arkstore_category_item.id))
    for item in data:
        arkstore_id = item.get('id')
        arkstore_name = item.get('name', '')
        arkstore_type = item.get('type', '')
        arkstore_parent_id = item.get('parent_id', None)

        arkstorecategory = ArkStoreCategory.valid_objects.filter(
            arkstore_id=arkstore_id
        ).first()
        if arkstorecategory is None:
            arkstorecategory = ArkStoreCategory()
            arkstorecategory.arkstore_id = arkstore_id
        arkstorecategory.arkstore_name = arkstore_name
        arkstorecategory.arkstore_type = arkstore_type
        arkstorecategory.arkstore_parent_id = arkstore_parent_id
        arkstorecategory.save()
        if str(arkstorecategory.id) in all_arkstore_category_ids:
            all_arkstore_category_ids.remove(str(arkstorecategory.id))
    if all_arkstore_category_ids:
        ArkStoreCategory.valid_objects.filter(id__in=all_arkstore_category_ids).delete()
    # 需要同步应用分类关系
    logging.info('同步arkstore分类')

@api.get("/tenant/{tenant_id}/arkstore/purchased/extensions/", tags=['方舟商店'], response=List[OnShelveExtensionPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(ArstoreExtensionPagination)
def list_arkstore_purchased_extensions(request, tenant_id: str, category_id: str = None):
    extra_params = {}
    if category_id and category_id != "" and category_id != "0":
        extra_params['category_id'] = category_id
    return get_arkstore_list(request, True, 'extension', extra_params=extra_params)


class ArkstoreStatusFilterIn(Schema):
    installed: Optional[bool] = Field(
        title=_("已安装")
    )
    has_upgrade: Optional[bool] = Field(
        title=_("有升级")
    )

@api.get("/tenant/{tenant_id}/arkstore/purchased_and_installed/extensions/", tags=['方舟商店'], response=List[OnShelveExtensionPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN,NORMAL_USER])
@paginate(CustomPagination)
def list_arkstore_purchased_and_installed_extensions(request, tenant_id: str, filter: ArkstoreStatusFilterIn=Query(...)):
    extra_params = {}
    installed_exts = Extension.valid_objects.filter().all()
    
    tenant_extension_ids = TenantExtension.valid_objects.filter(tenant_id=tenant_id, is_active=True).values('extension_id')
    tenant_active_extension_ids_set = {x['extension_id'] for x in tenant_extension_ids}
    for ext in installed_exts:
        ext.is_active_tenant = True if ext.id in tenant_active_extension_ids_set else False

    installed_ext_packages = {ext.package: ext for ext in installed_exts}
    purchased_exts = get_arkstore_list(request, True, 'extension', all=True, extra_params=extra_params)['items']
    for ext in purchased_exts:
        ext['arkstore_uuid'] = ext['uuid']
        if ext['package'] in installed_ext_packages:
            local_ext = installed_ext_packages[ext['package']]
            ext['local_uuid'] = str(local_ext.id)
            ext['installed'] = True
            ext['is_active'] = local_ext.is_active
            ext['is_active_tenant'] = local_ext.is_active_tenant
            if local_ext.version < ext['version']:
                ext['has_upgrade'] = True
        else:
            ext['local_uuid'] = None
            ext['installed'] = False

    purchased_exts_packages = {ext['package']: ext for ext in purchased_exts}
    local_exts = [ext for ext in installed_exts if ext.package not in purchased_exts_packages]
    for ext in local_exts:
        ext.uuid = str(ext.id)
        ext.labels = " ".join(ext.labels) if ext.labels else ""
        ext.is_default_extension = True
        ext.local_uuid = str(ext.id)
        ext.arkstore_uuid = None

    if filter.has_upgrade == True:
        return [ext for ext in purchased_exts if ext.get('has_upgrade') == True]

    if filter.installed == False:
        return [ext for ext in purchased_exts if ext.get('installed') == False]
    elif filter.installed == True:
        return local_exts + [ext for ext in purchased_exts if ext.get('installed') == True]

    return local_exts + purchased_exts


@api.get("/tenant/{tenant_id}/arkstore/rented/extensions/", tags=['方舟商店'], response=List[OnShelveExtensionPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_rented_extensions(request, tenant_id: str):
    tenant = Tenant.objects.get(id=tenant_id)
    extension_ids = TenantExtension.valid_objects.filter(tenant_id=tenant_id, is_rented=True).values('extension_id')
    extensions = Extension.valid_objects.filter().all()

    tenant_extension_ids = TenantExtension.valid_objects.filter(tenant_id=tenant_id, is_active=True).values('extension_id')
    tenant_active_extension_ids_set = {x['extension_id'] for x in tenant_extension_ids}
    for ext in extensions:
        ext.is_active_tenant = True if ext.id in tenant_active_extension_ids_set else False
    
    if settings.IS_CENTRAL_ARKID:
        return extensions

    for ext in extensions:
        ext.uuid = str(ext.id)
        ext.labels = " ".join(ext.labels) if ext.labels else ""

    if tenant.is_platform_tenant:
        for ext in extensions:
            ext.lease_useful_life = ["不限天数，不限人数"]
            ext.lease_state = '已租赁'
            ext.local_uuid = str(ext.id)
            ext.arkstore_uuid = None
        return extensions

    resp = get_arkstore_list(request, None, 'extension', rented=True, all=True)['items']
    extensions_rented = {ext['package']: ext for ext in resp}
    for ext in extensions:
        ext.local_uuid = str(ext.id)
        if ext.package in extensions_rented:
            ext_arkstore = extensions_rented[ext.package]
            ext.arkstore_uuid = ext_arkstore['uuid']
            ext.lease_useful_life = ext_arkstore['lease_useful_life']
            ext.lease_state = '已租赁'
            lease_records = ext_arkstore.get('lease_records') or []
            # check_lease_records_expired
            if check_time_and_user_valid(lease_records, tenant):
                tenant_extension, created = TenantExtension.objects.update_or_create(
                    tenant_id=tenant_id,
                    extension=ext,
                    defaults={"is_rented": True}
                )
        else:
            ext.arkstore_uuid = None

    return extensions


class PrivateAppPurchaseOut(ArkstoreAppItemSchemaOut):
    status: str = Field(
        default="",
        title=_('Status', "状态")
    )

@api.get("/tenant/{tenant_id}/arkstore/purchased/private_apps/", tags=['方舟商店'], response=List[PrivateAppPurchaseOut])
@operation(List[ArkstoreItemSchemaOut], roles=[PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_purchased_private_apps(request, tenant_id: str, category_id: str = None):
    extra_params = {}
    if category_id and category_id != "" and category_id != "0":
        extra_params['category_id'] = category_id
    extra_params['type'] = 'private_app'
    arkstore_private_apps = get_arkstore_list(request, True, 'app', all=True, extra_params=extra_params)['items']
    installed_apps = PrivateApp.active_objects.filter(tenant_id=tenant_id, arkstore_app_id__isnull=False)
    installed_apps_dict = {str(app.arkstore_app_id): app for app in installed_apps}
    for app in arkstore_private_apps:
        if app['uuid'] not in installed_apps_dict:
            app['status'] = '未安装'
        else:
            app['status'] = installed_apps_dict[app['uuid']].status
    return arkstore_private_apps


@api.get("/tenant/{tenant_id}/arkstore/purchased/apps/", tags=['方舟商店'], response=List[ArkstoreAppItemSchemaOut])
@operation(List[ArkstoreItemSchemaOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_arkstore_purchased_apps(request, tenant_id: str, category_id: str = None):
    extra_params = {}
    if category_id and category_id != "" and category_id != "0":
        extra_params['category_id'] = category_id
    extra_params['type'] = 'app'
    arkstore_apps = get_arkstore_list(request, None, 'app', all=True, extra_params=extra_params)['items']
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


@api.get("/tenant/{tenant_id}/arkstore/purchase/order/{order_no}/payment_status/extensions/{uuid}/", tags=['方舟商店'],
    response={
        200: PaymentStatus,
        202: ResponseSchema,
    })
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_order_payment_status_arkstore_extension(request, tenant_id: str, order_no: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = order_payment_status_arkstore_extension(access_token, order_no)
    if resp.get('code') == '0' and not resp.get('appid'):
        return 202, {'data': resp}
    else:
        # install extension
        if resp.get('trade_state') == 'SUCCESS':
            install_arkstore_extension(tenant, token, uuid)
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
    # install extension
    install_arkstore_extension(tenant, token, uuid)
    return {'data': resp}


@api.post("/tenant/{tenant_id}/arkstore/install/{uuid}/", tags=['方舟商店'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def install_arkstore_extension_from_arkstore(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = install_arkstore_extension(tenant, token, uuid)
    resp = {'error': ErrorCode.OK.value, 'data': {}}
    return resp


@api.post("/tenant/{tenant_id}/arkstore/update/{package}/", tags=['方舟商店'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_arkstore_extension_from_arkstore(request, tenant_id: str, package: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    ext_info = get_arkstore_extension_detail_by_package(access_token, package)
    if ext_info is None:
        return ErrorDict(ErrorCode.UPDATE_EXTENSION_SUCCESS)
    result = install_arkstore_extension(tenant, token, ext_info['uuid'])
    resp = {'error': ErrorCode.OK.value, 'data': {}}
    return resp


class CutomValuesData(Schema):
    values_data: Optional[str] = Field(
        default="",
        format='textarea',
        title=_('Values Data', '配置')
    )

class CustomAppValuesOut(ResponseSchema):
    data: CutomValuesData

@api.get("/tenant/{tenant_id}/arkstore/install/private_app/{uuid}/", tags=['方舟商店'], response=CustomAppValuesOut)
@operation(roles=[PLATFORM_ADMIN])
def get_private_app_custom_values(request, tenant_id: str, uuid: str):
    private_app = PrivateApp.active_objects.filter(arkstore_app_id=uuid).first()
    return {"data": {"values_data": private_app.values_data or ""}}


@api.post("/tenant/{tenant_id}/arkstore/install/private_app/{uuid}/", tags=['方舟商店'], response=ResponseSchema)
@operation(roles=[PLATFORM_ADMIN])
def install_private_app_from_arkstore(request, tenant_id: str, uuid: str, data: CutomValuesData):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = install_arkstore_private_app(tenant, token, uuid, data.values_data)
    if result['code'] == 0:
        return {'error': ErrorCode.OK.value, 'data': {}}
    if result['code'] == 1:
        return ErrorDict(ErrorCode.PRIVATE_APP_ALREADY_INSTALLED, message=result['message'])
    return ErrorDict(ErrorCode.PRIVATE_APP_INSTALL_FAILED, message=result['message'])


@api.delete("/tenant/{tenant_id}/arkstore/private_app/{uuid}/", tags=['方舟商店'], response=ResponseSchema)
@operation(roles=[PLATFORM_ADMIN])
def delete_private_app_from_arkstore(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = delete_arkstore_private_app(tenant, token, uuid)
    if result['code'] == 0:
        return {'error': ErrorCode.OK.value, 'data': {}}
    return ErrorDict(ErrorCode.PRIVATE_APP_DELETE_FAILED, message=result['message'])


class AppValuesSchema(Schema):
    values_data: str = Field(format='textarea', readonly=True)

class AppValuesOut(ResponseSchema):
    data: AppValuesSchema

@api.get("/tenant/{tenant_id}/arkstore/private_app/{uuid}/default_values/", tags=['方舟商店'], response=AppValuesOut)
@operation(roles=[PLATFORM_ADMIN])
def get_private_app_default_values(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    resp = get_arkstore_private_app_data(tenant, token, uuid)
    return {"data": resp}


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


@api.get("/tenant/{tenant_id}/arkstore/apps/{id}/click/", tags=['方舟商店'])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def arkstore_app_click(request, tenant_id: str, id: str):
    resp = {'error': ErrorCode.OK.value, 'data': {}}
    if settings.IS_CENTRAL_ARKID:
        return resp

    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    app = App.active_objects.get(id=id)
    if not app or not app.arkstore_app_id:
        return resp
    result = click_arkstore_app(access_token, app.arkstore_app_id)
    return resp


@api.get("/restart/", auth=None)
def restart(request):
    from arkid.core.models import Node
    
    # 限制内网访问
    ip = request.META.get('REMOTE_ADDR')
    if not Node.objects.filter(ip=ip).exists():
        return
    
    import os
    try:
        print("新安装的插件有models需重启django, 正在重启django server!")
        os.system("supervisorctl restart runserver")
    except Exception as e:
        print("未使用supervisor启动django server, 需手动重启django server!")
