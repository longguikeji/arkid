"""
statistic
"""
import datetime

from django.conf import settings

from oneid.utils import redis_conn
import time

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


class TimeCash:

    all_timer = {}

    @staticmethod
    def getInstance(name):
        if TimeCash.all_timer.get(name):
            return TimeCash.all_timer[name]
        timer = TimeCash(name)
        TimeCash.all_timer[name] = timer
        return timer

    @staticmethod
    def over():
        for name in TimeCash.all_timer:
            TimeCash.all_timer[name].end()

    def __init__(self,name):
        self.name = name
        self.count = {}
        self.timelist = {}
        self.zero = time.time()
        self.now = time.time()
        super().__init__()

    def pr(self,tag, *args, **kwargs):
        self.pre = self.now 
        self.now = time.time()
        self.count[tag] = self.count.get(tag,0) + 1
        self.timelist[tag] = self.timelist.get(tag,0) + (self.now - self.pre)
        # print( self.name ,tag, self.timelist.get(tag), (self.now - self.pre), *args, **kwargs)

    def end(self):
        for tag in self.timelist.keys():
            print( self.name, tag, self.count[tag], self.timelist.get(tag), time.time() - self.zero)