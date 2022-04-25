from arkid.core import routers,pages
from arkid.core.translation import gettext_default as _

tag = "grant_manage"
name = _("授权管理")

page = pages.TabsPage(
    tag=tag,
    name=name
)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path='grant_manage',
    name=_('授权管理'),
)