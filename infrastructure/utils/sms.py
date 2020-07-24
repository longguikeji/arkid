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
    _mobile = mobile.split(' ')
    if len(_mobile) != 2:
        return False
    # return bool(re.match(r'^\+[\d]{1,4} [\d]{2,20}$', mobile))
    return i18n_mobile_verify(_mobile[1], _mobile[0][1:])


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


def i18n_mobile_verify(mobile, state_code, state=None):
    """
    根据国际手机接入配置校验手机号
    """
    # pylint: disable=import-outside-toplevel
    from oneid_meta.models import I18NMobileConfig
    # 验证区号是否匹配
    config = I18NMobileConfig.valid_objects.filter(state_code=state_code).first()
    if not config:    # 未匹配任何配置
        return False
    if not config.is_active:    # 配置未启用
        return False
    if state is not None and config.state.lower() != state.lower():    # 匹配给定区域
        return False
    # 校验号码长度
    if config.number_length is not None and len(mobile) != config.number_length:
        return False
    # 校验首位数字
    if config.start_digital and int(mobile[0]) not in config.start_digital:
        return False
    return True
