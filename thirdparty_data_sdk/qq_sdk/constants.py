'''
QQ API URL
'''
from ...common.setup_utils import validate_attr
from ...oneid import settings
from sys import _getframe

validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno,
              'BASE_URL')
REDIRECT_URI = settings.BASE_URL + '/#/oneid/bindthirdparty/qq'
GET_TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
GET_OPENID_URL = 'https://graph.qq.com/oauth2.0/me'

# errcode msg map
APPID_KEY_VALID = '100005'
REDIRECT_URI_ILLEGAL = '100010'
