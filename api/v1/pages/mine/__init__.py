from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import profile, approve_manage,auth_manage,grant_manage,switch_tenant,logout

router = routers.FrontRouter(
    path='mine',
    name=_('我的'),
    children=[
        profile.router,
        auth_manage.router,
        grant_manage.router,
        approve_manage.router,
        switch_tenant.router,
        logout.router,
    ]
)

router.hidden = True