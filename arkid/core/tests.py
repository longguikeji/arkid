from django.test import TestCase

# Create your tests here.

SEND_SMS_CODE = 'SEND_SMS_CODE'

from pydantic import BaseModel

class SendSMSCodeDataModel(BaseModel):
    code: str

register(tag=SEND_SMS_CODE, name=_('发送短信验证码'), data_model=SendSMSCodeDataModel)

@listen_event([SEND_SMS_CODE])
def print_result(event, **kwargs):
    event.data.code = 'changed'
    return {'res': '456'}

@listen_event([SEND_SMS_CODE])
def print_result2(event, **kwargs):
    event.data = 'changed2'
    return {'res': '456'}

res = dispacth(Event(SEND_SMS_CODE, 'tenant', {'code':'1234'}))

