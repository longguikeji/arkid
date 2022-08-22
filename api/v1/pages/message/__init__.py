from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import message_manage,mine_message
router = routers.FrontRouter(
    path='message',
    name=_('消息中心'),
    icon='message',
    children=[
        message_manage.router,
        mine_message.router
    ]
)