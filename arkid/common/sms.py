import random
import string
from arkid.core.event import SEND_SMS, Event, dispatch_event
from django.core.cache import cache


def gen_sms_code(auth_code_length=6):
    return ''.join(random.choice(string.digits) for _ in range(auth_code_length))


def gen_sms_code_key(mobile):
    '''
    生成短信验证码的key
    '''
    return f'sms:{mobile}'


def send_sms(phone_number, tenant, request, config_id, template_params):
    """发送短信
    """
    data = {
        "phone_number": phone_number,
        "config_id": config_id,
        "template_params": template_params
    }
    return dispatch_event(Event(tag=SEND_SMS, tenant=tenant, request=request, data=data))


def send_sms_code(phone_number, tenant, request, config_id):
    """发送短信验证码
    """
    code = gen_sms_code()
    response = send_sms(phone_number, tenant, request, config_id, {"code": code})
    cache.set(gen_sms_code_key(phone_number), code)
    return response


def check_sms_code(mobile, code):
    """ 验证短信验证码
    """
    c_code = cache.get(gen_sms_code_key(mobile))
    return c_code == code
