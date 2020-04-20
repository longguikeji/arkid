'''
utils about mobile & sms
'''

import re

CN_MOBILE_PREFIX = '+86 '


def is_native_mobile(mobile):
    '''
    是否为默认格式（中国）手机号
    形如 `18812341234`
    '''
    return bool(re.match(r'^1[\d]{10}$', mobile))


def is_i18n_mobile(mobile):
    '''
    是否为国际格式手机号
    形如 `+86 18812341234`
    '''
    return bool(re.match(r'^\+[\d]{1,4} [\d]{2,20}$', mobile))


def is_mobile(mobile):
    '''
    是否为有效的手机号
    '''
    return is_native_mobile(mobile) or is_i18n_mobile(mobile)


def is_cn_mobile(mobile):
    '''
    是否为国内手机号
    '''
    return is_native_mobile(mobile) or \
        (
            is_i18n_mobile(mobile) and mobile.startswith(CN_MOBILE_PREFIX)
        )
