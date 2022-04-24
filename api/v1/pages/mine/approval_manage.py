# 审批管理
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

approve_action_tag = "approve_action"
approve_action_name = _("审批动作")


page = FormPage(
    name=approve_action_name,
    tag=approve_action_tag
)

register_front_pages(page)

router = router = FrontRouter(
    path=approve_action_tag,
    name=approve_action_name,
    icon='app',
    page=page,
)