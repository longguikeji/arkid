DEBUG = True

# Redis cache
REDISHOST = os.getenv("REDIS_HOST", "localhost")
REDISPASSWD = os.getenv("REDIS_PASSWD", None)

REDIS_CONFIG = {
    'HOST': REDISHOST,
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': REDISPASSWD,
}

REDIS_URL = 'redis://{}:{}/{}'.format(REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'],\
    REDIS_CONFIG['DB']) if REDIS_CONFIG['PASSWORD'] is None \
        else 'redis://:{}@{}:{}/{}'.format(REDIS_CONFIG['PASSWORD'],\
            REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB'])

# CELERY
CELERY_BROKER_URL = REDIS_URL
