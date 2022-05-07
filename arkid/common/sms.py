import random
import string
from arkid.core.event import SEND_SMS,Event,dispatch_event
from django.core.cache import cache

def gen_sms_code(auth_code_length=6):
    return ''.join(random.choice(string.digits) for _ in range(auth_code_length))

def gen_sms_code_key(mobile):
    '''
    生成短信验证码的key
    '''
    return f'sms:{mobile}'

def send_sms(mobile,message):
    dispatch_event(Event(SEND_SMS, 'tenant', {'code':'1234'}))
    
def send_sms_code(mobile,template_id="您的验证码是%s"):
    code = gen_sms_code()
    message = template_id % code
    send_sms(mobile,message)
    cache.set(gen_sms_code_key(mobile),code)
    
def check_sms_code(mobile, code):
    c_code = cache.get(gen_sms_code_key(mobile))
    return c_code == code