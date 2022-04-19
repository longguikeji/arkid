from ninja import Schema
from pydantic import Field
from arkid.core.api import api
from arkid.core.models import App
from django.db import transaction
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.extension.app_protocol import create_app_protocol_extension_config_schema
from arkid.core.event import CREATE_APP, UPDATE_APP, DELETE_APP

register_event(CREATE_APP, _('create app','创建应用'))
register_event(UPDATE_APP, _('update app','修改应用'))
register_event(DELETE_APP, _('delete app','删除应用'))

class AppConfigSchemaIn(Schema):
    pass

create_app_protocol_extension_config_schema(
    AppConfigSchemaIn,
)


class AppConfigSchemaOut(Schema):
    app_id: str


@transaction.atomic
@api.post("/{tenant_id}/app/", response=AppConfigSchemaOut, auth=None)
def create_app_config(request, tenant_id: str, data: AppConfigSchemaIn):
    # 此处多了一层data需要多次获取
    data = data.data
    tenant = request.tenant
    # 事件分发
    results = dispatch_event(Event(tag=CREATE_APP, tenant=tenant, request=request, data=data))
    for func, ((result, extension), item) in results:
        if result:
            # 创建config
            config = extension.create_tenant_config(tenant, data.config.dict())
            # 创建app
            app = App()
            app.name = data.name
            app.url = data.url
            app.logo = data.logo
            app.type = data.app_type
            app.description = data.description
            app.config = config
            app.tenant_id = tenant_id
            app.save()
            break
    return {"app_id": app.id.hex}