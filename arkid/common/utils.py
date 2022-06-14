import re
from copy import deepcopy
from functools import reduce
from typing import Dict, List
from uuid import uuid4
from arkid.core.models import ExpiringToken
from arkid.common.logger import logger
from django.utils.translation import gettext_lazy as _


def deep_merge(*dicts: List[Dict], update=False) -> Dict:
    """
    Merges dicts deeply.
    Parameters
    ----------
    dicts : list[dict]
        List of dicts.
    update : bool
        Whether to update the first dict or create a new dict.
    Returns
    -------
    merged : dict
        Merged dict.
    """

    def merge_into(d1: Dict, d2: Dict):
        for key in d2:
            if key not in d1 or not isinstance(d1[key], dict):
                d1[key] = deepcopy(d2[key])
            else:
                d1[key] = merge_into(d1[key], d2[key])
        return d1

    if update:
        return reduce(merge_into, dicts[1:], dicts[0])
    else:
        return reduce(merge_into, dicts, {})


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
    return is_native_mobile(mobile) or (
        is_i18n_mobile(mobile) and mobile.startswith(CN_MOBILE_PREFIX)
    )


def i18n_mobile_verify(mobile, state_code, state=None):
    return True
    """
    根据国际手机接入配置校验手机号
    """
    # pylint: disable=import-outside-toplevel
    from inventory.models import I18NMobileConfig

    # 验证区号是否匹配
    config = I18NMobileConfig.valid_objects.filter(state_code=state_code).first()
    if not config:  # 未匹配任何配置
        return False
    if not config.is_active:  # 配置未启用
        return False
    if state is not None and config.state.lower() != state.lower():  # 匹配给定区域
        return False
    # 校验号码长度
    if config.number_length is not None and len(mobile) != config.number_length:
        return False
    # 校验首位数字
    if config.start_digital and int(mobile[0]) not in config.start_digital:
        return False
    return True


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_password_complexity(pwd, tenant):
    from login_register_config.models import LoginRegisterConfig

    if not pwd:
        return False, 'No password provide'

    config = LoginRegisterConfig.active_objects.filter(
        tenant=tenant, data__is_apply=True
    ).first()
    if config:
        regular = config.data.get('regular')
        title = config.data.get('title')
        if re.match(regular, pwd):
            return True, None
        else:
            return False, title
    return True, None


def set_user_register_count(ip, check_str='register', time_limit=1):
    key = f'{ip}-{check_str}'
    runtime = get_app_runtime()
    data = runtime.cache_provider.get(key)
    if data is None:
        v = 1
    else:
        v = int(data) + 1
    runtime.cache_provider.set(key, v, time_limit * 60)


def get_user_register_count(ip, check_str='register'):
    key = f'{ip}-{check_str}'
    runtime = get_app_runtime()
    data = runtime.cache_provider.get(key)
    if data is None:
        return 0
    return int(data)


def get_password_error_count(ip, check_str='login'):
    key = f'{ip}-{check_str}'
    runtime = get_app_runtime()
    if runtime.cache_provider is None:
        return 0
    data = runtime.cache_provider.get(key)
    if data is None:
        return 0
    return int(data)


def mark_user_login_failed(ip, check_str='login'):
    key = f'{ip}-{check_str}'
    runtime = get_app_runtime()
    data = runtime.cache_provider.get(key)
    if data is None:
        v = 1
    else:
        v = int(data) + 1
    runtime.cache_provider.set(key, v, 86400)


def get_request_tenant(request):
    from tenant.models import Tenant

    tenant = None
    tenant_id = request.query_params.get('tenant', None)
    if tenant_id:
        tenant = Tenant.active_objects.filter(uuid=tenant_id).first()
    else:
        # 能够注册平台用户了
        tenant = Tenant.active_objects.filter(id=1).first()
    return tenant


global_tags = []


def gen_tag(tag: str = None, tag_pre: str = None) -> str:
    """生成tag

    Args:
        tag (str, optional): tag字符串，可指定亦可动态生成.
        tag_pre (str, optional): tag前缀，一般可为插件名称或者其他.

    Returns:
        str: tag字符串
    """
    tag = tag if tag else uuid4().hex
    tag = f"{tag_pre}_{tag}" if tag_pre else tag
    assert tag not in global_tags
    global_tags.append(tag)
    return tag


def verify_token(request):
    headers = request.headers
    auth_value = headers.get("Authorization")

    if not auth_value:
        return None
    parts = auth_value.split(" ")

    if parts[0].lower() != "token":
        return None
    token = " ".join(parts[1:])
    try:
        token = ExpiringToken.objects.get(token=token)

        if not token.user.is_active:
            raise Exception(_('User inactive or deleted', '用户无效或被删除'))

        if token.expired(request.tenant):
            raise Exception(_('Token has expired', '秘钥已经过期'))

    except ExpiringToken.DoesNotExist:
        logger.error(_("Invalid token", "无效的秘钥"))
        return None
    except Exception as err:
        logger.error(err)
        return None

    return token.user
