# 认证规则
from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

auth_rule_tag = 'auth_rule'
auth_rule_name = '认证规则'


page = pages.TablePage(
    tag=auth_rule_tag,
    name=auth_rule_name,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/auth_rules/',
        method=pages.FrontActionMethod.GET
    )
)

edit_page = pages.FormPage(
    name=_("编辑认证规则"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/auth_rules/{id}/',
        method=pages.FrontActionMethod.GET
    )
)

edit_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/auth_rules/{id}/",
            icon="icon-confirm"
        ),
        pages.FrontAction(
            name=_("取消"),
            action_type=pages.FrontActionType.CANCEL_ACTION,
            icon="icon-cancel"
        ),
        pages.FrontAction(
            name=_("重置"),
            action_type=pages.FrontActionType.RESET_ACTION,
            icon="icon-reset"
        ),
    ]
)

create_page = pages.FormPage(
    name=_("创建一个新的认证规则"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/auth_rules/',
        method=pages.FrontActionMethod.POST
    )
)

create_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/auth_rules/",
            action_type=pages.FrontActionType.DIRECT_ACTION,
            icon="icon-confirm"
        ),
        pages.FrontAction(
            name=_("取消"),
            action_type=pages.FrontActionType.CANCEL_ACTION,
            icon="icon-cancel"
        ),
        pages.FrontAction(
            name=_("重置"),
            action_type=pages.FrontActionType.RESET_ACTION,
            icon="icon-reset"
        ),
    ]
)

page.add_local_action(
    [
        pages.FrontAction(
            name=_("编辑"),
            page=edit_page,
            icon="icon-edit",
            action_type=pages.FrontActionType.OPEN_ACTION
        ),
        pages.FrontAction(
            name=_("删除"),
            method=pages.FrontActionMethod.DELETE,
            path="/api/v1/tenant/{tenant_id}/auth_rules/{id}/",
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

page.add_global_action(
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
    path=auth_rule_tag,
    name=auth_rule_name,
    page=page,
)

pages.register_front_pages(page)
pages.register_front_pages(create_page)
pages.register_front_pages(edit_page)