#!/usr/bin/env python3

"""
URL
"""

AUTHORIZE_URL = 'https://login.dingtalk.com/oauth2/auth?redirect_uri={}&response_type=code&client_id={}&scope=openid&state={}&prompt=consent'
GET_TOKEN_URL = 'https://api.dingtalk.com/v1.0/oauth2/userAccessToken'
GET_USERINFO_URL = 'https://api.dingtalk.com/v1.0/contact/users/me'

# errcode msg map
# CLIENT_VALID = 'bad_verification_code'


KEY = 'dingding'
# BIND_KEY = 'dingding_user_id'
# LOGIN_URL = 'github/login'
IMG_URL = 'https://img.alicdn.com/tfs/TB1yIubM6DpK1RjSZFrXXa78VXa-144-144.png'


# AUTHORIZE_URL = 'https://login.dingtalk.com/oauth2/auth?redirect_uri={}&response_type=code&client_id={}&scope=openid&state={}&prompt=consent'
# GET_TOKEN_URL = 'https://api.dingtalk.com/v1.0/oauth2/userAccessToken'
# GET_USERINFO_URL = 'https://api.dingtalk.com/v1.0/contact/users/me'
# FRESH_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={}&grant_type=refresh_token&refresh_token={}'


# # errcode msg map
# CLIENT_VALID = 'bad_verification_code'

# KEY = 'dingding'
# IMG_URL = 'https://img.alicdn.com/tfs/TB1yIubM6DpK1RjSZFrXXa78VXa-144-144.png'
