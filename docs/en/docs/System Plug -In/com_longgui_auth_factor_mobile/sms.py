import random
import string
from typing import Optional
from arkid.core.event import SEND_SMS, Event, dispatch_event
from arkid.common import cache


def gen_sms_code(auth_code_length=6):
    return ''.join(random.choice(string.digits) for _ in range(auth_code_length))

def gen_sms_code_key(mobile):
    '''
    生成短信验证码的key
    '''
    return f'sms:{mobile}'

def create_sms_code(tenant,phone_number,uth_code_length=6,expired:Optional[int]=None):
    """生成短信验证码并存储至缓存
    """
    code = gen_sms_code(uth_code_length)
    cache.set(tenant,gen_sms_code_key(phone_number), code, expired=expired)
    return code

def check_sms_code(tenant,mobile, code):
    """ 验证短信验证码
    """
    c_code = cache.get(tenant,gen_sms_code_key(mobile))
    return c_code == code
