# 应用协议
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

tag = "approve_system"
name = _("审批系统")


page = FormPage(name=name,tag=tag)

register_front_pages(page)

router = FrontRouter(
    path=tag,
    name=name,
    page=page,
)