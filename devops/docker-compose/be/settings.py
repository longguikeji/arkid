DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'arkid',
        'USER': 'root',
    # <----
        'PASSWORD': 'root',    # {.env.SQL_PWD}
        'HOST': 'arkid-db',    # {.env.INSTANCE}-db
    # ---->
        'PORT': '3306',
        'OPTIONS': {
            'autocommit': True,
            'init_command': 'SET default_storage_engine=InnoDB',
            'charset': 'utf8mb4',
        },
    }
}

REDIS_CONFIG = {
    # <----
    'HOST': 'arkid-redis',    # {.env.INSTANCE}-redis
    # ---->
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}
REDIS_URL = 'redis://{}:{}/{}'.format(REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB']) if REDIS_CONFIG['PASSWORD'] is None \
        else 'redis://:{}@{}:{}/{}'.format(REDIS_CONFIG['PASSWORD'], REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB'])
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 60 * 60 * 24 * 3,
        "OPTIONS": {
            "MAX_ENTRIES": None,
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
CELERY_BROKER_URL = REDIS_URL

INSTALLED_APPS += ['ldap.sql_backend']

# 最终对外暴露的 web server 地址
# <----
BASE_URL = 'http://localhost'
# ---->
