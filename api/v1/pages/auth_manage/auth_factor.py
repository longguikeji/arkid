# 认证因素
from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

auth_factor_tag = 'auth_factor'
auth_factor_name = '认证因素'


page = pages.TablePage(
    tag=auth_factor_tag,
    name=auth_factor_name,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/auth_factor/',
        method=pages.FrontActionMethod.GET
    )
)

create_page = pages.FormPage(
    name=_("创建一个新的认证因素"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/auth_factor/',
        method=pages.FrontActionMethod.POST
    )
)

create_page.add_global_actions(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/auth_factor/",
            action_type=pages.FrontActionType.DIRECT_ACTION,
            icon="icon-confirm"
        ),
        pages.CancelAction(),
        pages.ResetAction(),
    ]
)

page.add_global_actions(
    [
        pages.FrontAction(
            name="创建",
            page=create_page,
            icon="icon-create",
            action_type=pages.FrontActionType.OPEN_ACTION
        )
    ]
)


router = routers.FrontRouter(
    path=auth_factor_tag,
    name=auth_factor_name,
    page=page,
)

pages.register_front_pages(page)
pages.register_front_pages(create_page)