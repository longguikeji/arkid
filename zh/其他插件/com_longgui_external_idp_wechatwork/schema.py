from ninja import Schema
from pydantic import Field
from arkid.core.translation import gettext_default as _


class WechatworkConfigBaseSchema(Schema):

    corpid: str = Field(title=_('Corp ID', '企业ID'))
    corpsecret: str = Field(title=_('Corp Secret', '应用密钥'))

    img_url: str = Field(title=_('Img URL', '图标URL'), format='upload', default='')
    login_url: str = Field(title=_('Login URL', '登录URL'), readonly=True, default='')
    callback_url: str = Field(
        title=_('Callback URL', '回调URL'), readonly=True, default=''
    )
    bind_url: str = Field(title=_('Bind URL', '绑定URL'), readonly=True, default='')