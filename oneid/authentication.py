'''
authentications
- HeaderArkerBaseAuthentication
'''
from rest_framework.authentication import BaseAuthentication
from django.conf import settings

from oneid_meta.models import User


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
