'''
authentications
- HeaderArkerBaseAuthentication
'''
from rest_framework.authentication import BaseAuthentication
from django.conf import settings

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


class CustomExpiringTokenAuthentication(ExpiringTokenAuthentication):
    '''
    自定义token校验
    '''
    def authenticate_credentials(self, key):
        '''
        在校验 token 基础上记录活跃程度
        '''
        user, token = super().authenticate_credentials(key)
        UserStatistics.set_active_count(user)
        user.update_last_active_time()
        return user, token
