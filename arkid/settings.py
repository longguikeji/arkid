"""
Django settings for arkid project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path
import common.monkeypatch
from arkid.spectacular_settings import SPECTACULAR_SETTINGS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y)c6vgiyu#-yll0#&kn!c0^t#2pqx_45w-b#sg2)asv+j_5pro'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TESTING = False    # always False

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_hotp',
    'django_otp.plugins.otp_static',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_expiring_authtoken',
    'drf_spectacular',
    'common',
    'tenant',
    'inventory',
    'app',
    'oauth2_provider',
    'tasks',
    'webhook',
    'siteadmin',
    'provisioning',
    'external_idp',
    'schema',
    'extension',
    'api',
    'system',
    'extension_root.github',
    'extension_root.gitee',
    'extension_root.feishu',
    'extension_root.mysql_migration',
    'extension_root.arkid',
    'django_scim',
    'extension_root.miniprogram',
]

# X_FRAME_OPTIONS = 'SAMEORIGIN'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_scim.middleware.SCIMAuthCheckMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    # Uncomment following if you want to access the admin
    'django.contrib.auth.backends.ModelBackend'
)

ROOT_URLCONF = 'arkid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'arkid.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_expiring_authtoken.authentication.ExpiringTokenAuthentication',
    ),
    # 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'


CELERY_BROKER = 'redis://localhost:6379'


AUTH_USER_MODEL = 'inventory.User'

CONFIG_FILE = 'arkid.toml'
CONFIG_LOCAL_FILE = 'arkid.local.toml'

OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    "SCOPES": {
        "openid": "OpenID Connect scope",
        "userinfo": "UserInfo"
        # ... any other scopes that you use
    },
    "OIDC_RSA_PRIVATE_KEY": """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCIThjbTwpYu4Lwqp8oA7PqD6Ij/GwpLFJuPbWVaeCDaX6T7mh8
mJMIEgl/VIZasLH8SwU5mZ4sPeiqk7NgJq1XDo97q5mlFoNVHMCH38KQzSIBWtbq
WnEEnQdiqBbCmmIebLd4OcfpbIVUI89cnCq7U0M1ie0KOopWSHWOP6/35QIDAQAB
AoGBAIdwmtBotM5A3LaJxAY9z6uXhzSc4Vj0OqBiXymtgDL0Q5t4/Yg5D3ioe5lz
guFgzCr23KVEmOA7UBMXGtlC9V+iizVSbF4g2GqPLBKk+IYcAhfbSCg5rbbtQ5m2
PZxKZlJOQnjFLeh4sxitd84GfX16RfAhsvIiaN4d4CG+RAlhAkEA1Vitep0aHKmA
KRIGvZrgfH7uEZh2rRsCoo9lTxCT8ocCU964iEUxNH050yKdqYzVnNyFysY7wFgL
gsVzPROE6QJBAKOOWj9mN7uxhjRv2L4iYJ/rZaloVA49KBZEhvI+PgC5kAIrNVaS
n1kbJtFg54IS8HsYIP4YxONLqmDuhZL2rZ0CQQDId9wCo85eclMPxHV7AiXANdDj
zbxt6jxunYlXYr9yG7RvNI921HVo2eZU42j8YW5zR6+cGusYUGL4jSo8kLPJAkAG
SLPi97Rwe7OiVCHJvFxmCI9RYPbJzUO7B0sAB7AuKvMDglF8UAnbTJXDOavrbXrb
3+N0n9MAwKl9K+zp5pxpAkBSEUlYA0kDUqRgfuAXrrO/JYErGzE0UpaHxq5gCvTf
g+gp5fQ4nmDrSNHjakzQCX2mKMsx/GLWZzoIDd7ECV9f
-----END RSA PRIVATE KEY-----""",
    # ... any other settings you want
}

LDAP_PORT = 389
SLAPD_PASSWORD = 'admin'
SLAPD_DOMAIN = 'dc=example,dc=org'
AUTH_USER_MODEL = 'inventory.User'

import os

# 引入settings_local.py 本地配置文件
if os.path.exists(os.path.join(BASE_DIR, 'settings_local.py')):
    exec(open(os.path.join(BASE_DIR, 'settings_local.py')).read())

# django-scim2
SCIM_SERVICE_PROVIDER = {
    'NETLOC': 'localhost',
    'AUTHENTICATION_SCHEMES': [
        {
            'type': 'oauth2',
            'name': 'OAuth 2',
            'description': 'Oauth 2 implemented with bearer token',
        },
    ],
    'GROUP_MODEL': 'inventory.models.Group',
    'USER_ADAPTER': 'inventory.adapters.ArkidSCIMUser',
    'GROUP_ADAPTER': 'inventory.adapters.ArkidSCIMGroup',
    'GROUP_FILTER_PARSER': 'inventory.filters.GroupFilterQuery',
    'USER_FILTER_PARSER': 'inventory.filters.UserFilterQuery'
}


# Celery settings

CELERY_BROKER_URL = 'redis://localhost'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
# CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'
# CELERY_TASK_SERIALIZER = 'json'
