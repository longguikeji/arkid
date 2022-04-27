from arkid.core import routers
from arkid.core.translation import gettext_default as _

router = routers.FrontRouter(
    path='mine',
    name=_('我的'),
    children=[
    ]
)

router.hidden = True