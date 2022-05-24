from arkid.core import routers,pages
from arkid.core.translation import gettext_default as _
from . import user_grant,group_grant,app_grant
tag = "grant_manage"
name = _("授权管理")

page = pages.TabsPage(
    tag=tag,
    name=name,
    pages=[
        user_grant.page,
        group_grant.page,
        app_grant.page
    ]
)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path='grant_manage',
    name=_('授权管理'),
    page=page,
    icon='grant',
)