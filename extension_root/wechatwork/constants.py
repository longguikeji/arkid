AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope=snsapi_base&state={}#wechat_redirect'
GET_TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'
GET_USERINFO_URL = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={}&code={}'
# errcode msg map
CLIENT_VALID = 'bad_verification_code'

KEY = 'wechatwork'
IMG_URL = 'https://img.onlinedown.net/download/202108/151913-611379f149740.jpg'
