import random
import string
from typing import Optional
from arkid.common import cache

def gen_email_code(auth_code_length=6):
    return ''.join(random.choice(string.digits) for _ in range(auth_code_length))

def gen_email_code_key(email):
    '''
    生成短信验证码的key
    '''
    return f'email:{email}'

def create_email_code(tenant,email,uth_code_length=6,expired:Optional[int]=None):
    """生成短信验证码并存储至缓存
    """
    code = gen_email_code(uth_code_length)
    cache.set(tenant,gen_email_code_key(email), code, expired=expired)
    return code

def check_email_code(tenant,email, code):
    """ 验证短信验证码
    """
    c_code = cache.get(tenant,gen_email_code_key(email))
    return c_code == code
