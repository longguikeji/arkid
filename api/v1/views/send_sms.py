from arkid.core.event import register_event, dispatch_event, Event
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.token import refresh_token
from arkid.core.error import ErrorCode
from api.v1.schema.auth import AuthIn, AuthOut
from arkid.core.event import SEND_SMS
from ninja import Schema
from arkid.common import sms

class SendSMSIn(Schema):
    config_id: str
    phone_number: str
    template_params: str
    # ('template_param', Optional[str], Field(title=_("TemplateParam", "短信模板变量对应的实际值"))),


@api.post("/tenant/{tenant_id}/send_sms/", tags=['发送短信'], auth=None)
@operation(AuthOut, use_id=True)
def send_sms(request, tenant_id: str, data: SendSMSIn):
    tenant = request.tenant
    responses = sms.send_sms(
        data.phone_number,
        tenant,
        request,
        data.config_id,
        data.template_params,
    )
    if not responses:
        return {'error': 'error_code', 'message': '认证插件未启用'}
    useless, (data, extension) = responses[0]
    return data


class SendSMSCodeIn(Schema):
    config_id: str
    phone_number: str

@api.post("/tenant/{tenant_id}/send_sms_code/", tags=['发送短信验证码'], auth=None)
@operation(AuthOut, use_id=True)
def send_sms_code(request, tenant_id: str, data: SendSMSCodeIn):
    """ 发送短信验证码
    """
    tenant = request.tenant

    responses = sms.send_sms_code(
        data.phone_number,
        tenant,
        request,
        data.config_id
    )
    if not responses:
        return {'error': 'error_code', 'message': '认证插件未启用'}
    useless, (data, extension) = responses[0]
    return data
