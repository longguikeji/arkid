# 审批系统
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

approve_system_tag = "approve_system"
approve_system_name = _("审批系统")


page = FormPage(
    name=approve_system_name,
    tag=approve_system_tag
)

register_front_pages(page)

router = router = FrontRouter(
    path=approve_system_tag,
    name=approve_system_name,
    icon='app',
    page=page,
)