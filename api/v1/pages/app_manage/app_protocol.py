# 应用协议
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

tag = "app_protocol"
name = _("应用协议")


page = FormPage(name=name,tag=tag)

register_front_pages(page)

router = FrontRouter(
    path=tag,
    name=name,
    icon='app',
    page=page,
)

