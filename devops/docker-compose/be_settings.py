import pymysql
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'arkid',
        'USER': 'root',
        'PASSWORD': '${SQL_PWD}',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'autocommit': True,
            'init_command': 'SET default_storage_engine=MyISAM',
        },
    }
}

INSTALLED_APPS += ['ldap.sql_backend']
BASE_URL = 'http://localhost'
