from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import profile, approve_manage,auth_manage,grant_manage,switch_tenant,logout,mine_message

router = routers.FrontRouter(
    path='mine',
    name=_('我的'),
    icon='mine',
    children=[
        profile.router,
        auth_manage.router,
        grant_manage.router,
        approve_manage.router,
        mine_message.router,
        switch_tenant.router,
        logout.router,
    ],
    mobile=True,
)

router.hidden = True