from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import grant_rules,permission_group,permission_list,grant_manage

router = routers.FrontRouter(
    path='permission_manage',
    name=_('权限管理'),
    icon='list',
    children=[
        permission_list.router,
        permission_group.router,
        grant_manage.router,
        grant_rules.router,
    ]
)