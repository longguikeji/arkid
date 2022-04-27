from arkid.core.event import register_event, dispatch_event, Event
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.token import refresh_token
from arkid.core.error import ErrorCode
from api.v1.schema.auth import AuthIn, AuthOut
from arkid.core.event import SEND_SMS
from ninja import Schema


class SendSMSIn(Schema):
    config_id: str
    phone_number: str
    template_params: str
    # ('template_param', Optional[str], Field(title=_("TemplateParam", "短信模板变量对应的实际值"))),


@api.post("/tenant/{tenant_id}/send_sms/", tags=['发送短信'], auth=None)
@operation(AuthOut, use_id=True)
def send_sms(request, tenant_id: str, data: SendSMSIn):
    tenant = request.tenant

    responses = dispatch_event(Event(tag=SEND_SMS, tenant=tenant, request=request, data=data))
    if not responses:
        return {'error': 'error_code', 'message': '认证插件未启用'}
    useless, (data, extension) = responses[0]
    return data
