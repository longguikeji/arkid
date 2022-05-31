from arkid.core.translation import gettext_default as _
from arkid.core import actions, pages, routers

tag = "mine_profile"
name = _("个人管理")

page = pages.TabsPage(tag=tag, name=name)
profile_page = pages.DescriptionPage(name=_('个人资料'))
edit_profile_page = pages.FormPage(name=_("更新个人资料"))

pages.register_front_pages(page)
pages.register_front_pages(profile_page)
pages.register_front_pages(edit_profile_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='profile',
)

page.add_pages([profile_page])

edit_profile_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/profile/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'confirm': actions.ConfirmAction(
            path="/api/v1/mine/tenant/{tenant_id}/profile/"
        ),
    },
)

profile_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/profile/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "edit": actions.OpenAction(
            name="编辑",
            page=edit_profile_page,
        ),
    },
)
