from arkid.core.translation import gettext_default as _
from arkid.core import actions, pages, routers

tag = "mine_profile"
name = _("个人资料")

page = pages.FormPage(
    tag=tag,
    name=name
)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/mine/tenant/{tenant_id}/profile/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions = [
        actions.ConfirmAction(path="/mine/tenant/{tenant_id}/profile/"),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)