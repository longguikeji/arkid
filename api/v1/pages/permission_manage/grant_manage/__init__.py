from arkid.core import routers
from arkid.core.translation import gettext_default as _

router = routers.FrontRouter(
    path='grant_manage',
    name=_('授权管理'),
    children=[
    ]
)