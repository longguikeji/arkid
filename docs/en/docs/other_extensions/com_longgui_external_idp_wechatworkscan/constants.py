#!/usr/bin/env python3

"""
URL
"""

AUTHORIZE_URL = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid={}&agentid={}&redirect_uri={}&state={}'
GET_TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'
GET_USERINFO_URL = (
    'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={}&code={}'
)

# errcode msg map
# CLIENT_VALID = 'bad_verification_code'


KEY = 'wechatworkscan'
# BIND_KEY = 'dingding_user_id'
# LOGIN_URL = 'github/login'
IMG_URL = 'https://wwcdn.weixin.qq.com/node/wwnl/wwnl/style/images/independent/favicon/favicon_32h.png'


# AUTHORIZE_URL = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid={}&agentid={}&redirect_uri={}&state={}'
# GET_TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'
# GET_USERINFO_URL = (
#     'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={}&code={}'
# )
# # errcode msg map
# CLIENT_VALID = 'bad_verification_code'

# KEY = 'wechatworkscan'
# IMG_URL = 'https://img.onlinedown.net/download/202108/151913-611379f149740.jpg'
