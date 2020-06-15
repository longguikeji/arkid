'''
authentications
- HeaderArkerBaseAuthentication
'''
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from drf_expiring_authtoken.authentication import ExpiringTokenAuthentication
from oneid_meta.models import User
from oneid.statistics import UserStatistics


class HeaderArkerBaseAuthentication(BaseAuthentication):
    '''
    auth by header['HTTP_ARKER']
    '''
    def authenticate(self, request):
        '''
        auth by header['HTTP_ARKER']
        '''
        arker = request.META.get('HTTP_ARKER', None)
        if arker in settings.CREDIBLE_ARKERS:
            return (self.get_user(request), None)

    @staticmethod
    def get_user(request):    # pylint: disable=unused-argument
        '''
        目前返回admin
        后续支持sudo模式，可按需返回指定user
        '''
        return User.valid_objects.get(username='admin')


class BaseExpiringTokenAuthentication(ExpiringTokenAuthentication):
    '''
    自定义token校验
    '''
    def authenticate_credentials(self, key):
        '''
        在校验 token 基础上记录活跃程度
        '''
        user, token = super().authenticate_credentials(key)
        if not settings.TESTING and not user.is_admin:
            UserStatistics.set_active_count(user)
            user.update_last_active_time()
        return user, token


class CustomExpiringTokenAuthentication(BaseExpiringTokenAuthentication):
    '''
    默认配置
    - 记录活跃程度
    - ...
    '''


class SUDOExpiringTokenAuthentication(BaseExpiringTokenAuthentication):
    '''
    支持 admin 使用 sudo 模式，以他人身份调用接口

    用于作为其他系统的子部分时的场景
    '''
    def authenticate(self, request):
        res = super().authenticate(request)
        if not res:
            return res

        user, token = res
        if user.is_admin:
            sudo = request.META.get('HTTP_SUDO', "")
            if sudo:
                target = User.valid_objects.filter(username=sudo).first()
                if target:
                    return target, token
                msg = _("Invalid SUDO")
                raise exceptions.AuthenticationFailed(msg)
        return user, token
