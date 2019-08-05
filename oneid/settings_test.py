"""
Only for testcases.
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(os.path.join(BASE_DIR, 'oneid', 'settings.py')):
    exec(open(os.path.join(BASE_DIR, 'oneid', 'settings.py')).read())

TESTING = True
EXECUTERS = [    # 注意顺序
    'executer.RDB.RDBExecuter',
    'executer.log.rdb.RDBLogExecuter',
    # 'executer.cache.default.CacheExecuter',
    # 'executer.LDAP.LDAPExecuter',
    # 'executer.Ding.DingExecuter',
]
