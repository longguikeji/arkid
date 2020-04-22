"""
Only for testcases.
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(os.path.join(BASE_DIR, 'oneid', 'settings.py')):
    exec(open(os.path.join(BASE_DIR, 'oneid', 'settings.py')).read())

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
    # 'oneid.authentication.CustomExpiringTokenAuthentication',
        'oneid.authentication.SUDOExpiringTokenAuthentication',
        'oneid.authentication.HeaderArkerBaseAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'oneid.permissions.IsAdminUser',
    )
}

TESTING = True
EXECUTERS = [    # 注意顺序
    'executer.RDB.RDBExecuter',
    'executer.log.rdb.RDBLogExecuter',
    # 'executer.cache.default.CacheExecuter',
    # 'executer.LDAP.LDAPExecuter',
    # 'executer.Ding.DingExecuter',
]

LANGUAGE_CODE = 'en'
BASE_URL = 'http://localhost'

#cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
