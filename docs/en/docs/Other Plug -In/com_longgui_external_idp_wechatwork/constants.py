#!/usr/bin/env python3

"""
URL
"""

AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope=snsapi_base&state={}#wechat_redirect'
GET_TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'
GET_USERINFO_URL = (
    'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={}&code={}'
)


KEY = 'wechatwork'
IMG_URL = 'https://wwcdn.weixin.qq.com/node/wwnl/wwnl/style/images/independent/favicon/favicon_32h.png'
