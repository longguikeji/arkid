"""
statistic
"""
import datetime

from django.conf import settings

from oneid.utils import redis_conn


class UserStatistics:
    """user statistics"""
    @staticmethod
    def get_active_count():
        '''
        get active count from cache
        '''
        date = datetime.datetime.today().date().isoformat()
        key = settings.ACTIVE_USER_REDIS_KEY_PREFIX + date
        count = redis_conn.hlen(key)
        if count:
            return count
        return 0

    @staticmethod
    def set_active_count(user):
        '''
        update active_count to cache
        '''
        date = datetime.datetime.today().date().isoformat()
        uuid = str(user.uuid)
        key = settings.ACTIVE_USER_REDIS_KEY_PREFIX + date
        res = redis_conn.hgetall(key)

        if res:
            redis_conn.hincrby(key, uuid, 1)
        else:
            redis_conn.hset(key, uuid, 1)
            redis_conn.expire(key, settings.ACTIVE_USER_DATA_LIFEDAY * 60 * 60 * 24)
