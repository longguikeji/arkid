from arkid.core.translation import gettext_default as _
from arkid.core import routers,pages
from arkid.core.pages import TabsPage

tag = "mine_auth_manage"
name = _("认证管理")

page = TabsPage(
    name=name,
    tag=tag
)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='auth',
    page=page
)