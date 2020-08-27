'''
通用检验函数
'''
import re


def username_valid(username):
    '''
    检验用户名格式.4-16位小写字母数字
    '''
    if re.match(r'^[a-z0-9]{4,32}$', username):
        return True
    return False
