'''
QQ API URL
'''
from oneid import settings

REDIRECT_URI = settings.BASE_URL + '/#/oneid/bindthirdparty/qq'
GET_TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
GET_OPENID_URL = 'https://graph.qq.com/oauth2.0/me'

# errcode msg map
APPID_KEY_VALID = '100005'
REDIRECT_URI_ILLEGAL = '100010'
