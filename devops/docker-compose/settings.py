# mysql database

MYSQLHOST = os.getenv("MYSQL_HOST", "localhost")
MYSQLPORT = os.getenv("MYSQL_PORT", "3306")
MYSQLDATABASE = os.getenv("MYSQL_DATABASE", "arkid")
MYSQLUSER = os.getenv("MYSQL_USER", "root")
MYSQLPASSWORD = os.getenv("MYSQL_PASSWORD", "root")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQLDATABASE,
        'HOST': MYSQLHOST,    # {.env.INSTANCE}-db
        'PORT': MYSQLPORT,
        'USER': MYSQLUSER,
        'PASSWORD': MYSQLPASSWORD,    # {.env.SQL_PWD}
        'OPTIONS': {
            'autocommit': True,
            'init_command': 'SET default_storage_engine=InnoDB',
            'charset': 'utf8mb4',
        },
    }
}

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


#CACHES = {
#    "default": {
#        "BACKEND": "django_redis.cache.RedisCache",
#        "LOCATION": REDIS_URL,
#        "TIMEOUT": 60 * 60 * 24 * 3,
#        "OPTIONS": {
#            "MAX_ENTRIES": None,
#            "CLIENT_CLASS": "django_redis.client.DefaultClient",
#        }
#    }
#}

# CELERY
CELERY_BROKER_URL = REDIS_URL

