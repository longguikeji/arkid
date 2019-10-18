# pylint: disable=undefined-variable, wrong-import-position, line-too-long
'''
settings.py 自定义配置示例

此示例涉及外的配置，除非明确知晓后果，否则不建议修改
建议在项目根路径下创建 settings_local.py，并只声明修改的部分。ArkID 将会加载此配置并追加覆盖到 settings.py
'''

# SECURITY

# - 正式环境中请重新生成 SECRET_KEY
## > In [1]: from django.core.management.utils import get_random_secret_key
## > In [2]: get_random_secret_key()
## > Out[2]: '$_&vn(0rlk+j7+cpq$$d=2(c1r(_8(c13ey51nslmm_nr6ov(t'
SECRET_KEY = "$_&vn(0rlk+j7+cpq$$d=2(c1r(_8(c13ey51nslmm_nr6ov(t"

# - 并关闭 debug 模式
DEBUG = False

# DATABASES

# - 默认使用 sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'db.sqlite3'),
    }
}

# - 正式环境推荐使用 MySQL
## client 为 pymysql，已在 requirements 中声明
## 若使用其他 client，需自行安装依赖
import pymysql
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'database_name',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'autocommit': True,
            'init_command': 'SET default_storage_engine=MyISAM',
        },
    }
}

# DOMAIN && IP
# - 内网IP
PRIVATE_IP = '192.168.0.150'
# - 公网IP
PUBLIC_IP = '47.111.105.142'
# - 访问地址
## 如果不能被公网访问将会影响部分需与第三方交互的功能，比如钉钉扫码登录等
BASE_URL = 'https://arkid.longguikeji.com'
BAES_URL = "http://47.111.105.142"

# storage
# - 目前一律文件存储于 minio 中，minio 的搭建不在此讨论范畴
MINIO_ENDPOINT = 'minio.longguikeji.com'
MINIO_ACCESS_KEY = '****'
MINIO_SECRET_KEY = '****'
MINIO_SECURE = True
MINIO_LOCATION = 'us-east-1'
MINIO_BUCKET = 'arkid'

# - 本地文件
## TODO：接下来将会支持基于本地文件系统的文件存储

# Redis
REDIS_CONFIG = {
    'HOST': '192.168.0.147',
    'PORT': 6379,
    'DB': 7,
    'PASSWORD': 'password',
}
## REDIS_URL, CACHES, CELERY_BROKER_URL 均依赖于 REDIS_CONFIG
## 如果在 settings_local 文件中修改了 REDIS_CONFIG，上述变量需重新声明，使 REDIS_CONFIG 的改动生效。
REDIS_URL = 'redis://{}:{}/{}'.format(REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB']) if REDIS_CONFIG['PASSWORD'] is None \
        else 'redis://:{}@{}:{}/{}'.format(REDIS_CONFIG['PASSWORD'], REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'], REDIS_CONFIG['DB'])
CACHES["default"]["LOCATION"] = REDIS_URL
CELERY_BROKER_URL = REDIS_URL

# LDAP

# - 启用 sql_backend ldap
## 需安装 ArkID  > docker pull longguikeji/ark-sql-ldap:1.0.0
## 且 database 为 MySQL
## 此时所有针对 LDAP_* 的配置均不对 LDAP server 生效。只读。
## TODO：支持LDAP_BASE、LDAP_PASSWORD 可修改。
INSTALLED_APPS += ['ldap.sql_backend']

## LDAP server 的访问地址，用于展示
LDAP_SERVER = 'ldap://localhost'
LDAPS_SERVER = 'ldaps://localhost'

# - 启用 native ldap (不建议使用)
## 需已有 LDAP server 且 LDAP 内没有数据
## 各对接信息按 此 LDAP server 实际情况填写
EXECUTERS += ['executer.LDAP.LDAPExecuter']

LDAP_SERVER = 'ldap://192.168.3.9'
LDAPS_SERVER = 'ldaps://192.168.3.9'
LDAP_BASE = 'dc=longguikeji,dc=com'
LDAP_USER = 'cn=admin,dc=longguikeji,dc=com'
LDAP_PASSWORD = 'admin'
## 此三项由arkid生成，只读。应依赖于LDAP_BASE,故需重新声明
LDAP_USER_BASE = 'ou=people,{}'.format(LDAP_BASE)
LDAP_DEPT_BASE = 'ou=dept,{}'.format(LDAP_BASE)
LDAP_GROUP_BASE = 'cn=intra,ou=group,{}'.format(LDAP_BASE)

# 钉钉
# - 向钉钉同步数据
EXECUTERS += ['executer.Ding.DingExecuter']
