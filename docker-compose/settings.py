DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'arkid',
        'HOST': 'arkid-db',
        'PORT': 3306,
        'USER': 'arkid',
        'PASSWORD': 'arkid',
        'OPTIONS': {
            'autocommit': True,
            'init_command': 'SET default_storage_engine=InnoDB',
            'charset': 'utf8mb4',
        },
    }
}

REDIS_CONFIG = {
    'HOST': 'arkid-redis',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}

REDIS_URL = 'redis://{}:{}/{}'.format(REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'],\
    REDIS_CONFIG['DB']) if REDIS_CONFIG['PASSWORD'] is None \
        else 'redis://:{}@{}:{}/{}'.format(REDIS_CONFIG['PASSWORD'],\
            REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB'])

# CELERY
CELERY_BROKER_URL = REDIS_URL
