'''
authentications
- HeaderArkerBaseAuthentication
'''
from rest_framework.authentication import BaseAuthentication
from drf_expiring_authtoken.authentication import ExpiringTokenAuthentication
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


class CustomExpiringTokenAuthentication(ExpiringTokenAuthentication):
    def authenticate_credentials(self, key):
        import datetime
        import redis
        user, token = super().authenticate_credentials(key)
        date = datetime.datetime.today().date().isoformat()
        if hasattr(token.user, 'uuid'):
            uuid = str(token.user.uuid)
            redis_conn = redis.Redis(settings.REDIS_HOST)
            key = 'active-' + date
            res = redis_conn.hgetall(key)

            if res:
                test_uuid = redis_conn.hget(key, uuid)
                if not test_uuid:
                    redis_conn.hincrby(key, uuid, 1)
                else:
                    redis_conn.hincrby(key, uuid, 1)
            else:
                redis_conn.hset(key, uuid, 1)
                redis_conn.expire(key, settings.ACTIVE_USER_DATA_LIFEDAY * 60 * 60 * 24)
        return user, token
