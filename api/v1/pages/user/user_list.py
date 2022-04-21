from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

user_list_tag = 'user_list'
user_list_name = '用户列表'


router = routers.FrontRouter(
    path=user_list_tag,
    name='用户管理',
    icon='user',
    page=user_list_tag,
)


page = pages.FrontPage(
    tag=user_list_tag,
    name=user_list_name,
    page_type=pages.FrontPageType.TABLE_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=pages.FrontActionMethod.GET
    )
)

user_edit_page = pages.FrontPage(
    name=_("编辑用户"),
    page_type=pages.FrontPageType.FORM_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/{id}/',
        method=pages.FrontActionMethod.GET
    )
)

user_edit_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/users/{id}/",
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

user_create_page = pages.FrontPage(
    name=_("创建一个新的用户"),
    page_type=pages.FrontPageType.FORM_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=pages.FrontActionMethod.POST
    )
)

user_create_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/users/",
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
            page=user_edit_page,
            icon="icon-edit",
            action_type=pages.FrontActionType.OPEN_ACTION
        ),
        pages.FrontAction(
            name=_("删除"),
            method=pages.FrontActionMethod.DELETE,
            path="/api/v1/tenant/{tenant_id}/users/{id}/",
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

page.add_global_action(
    [
        pages.FrontAction(
            name="创建",
            page=user_create_page,
            icon="icon-create",
            action_type=pages.FrontActionType.OPEN_ACTION
        )
    ]
)

pages.register_front_pages(page)
pages.register_front_pages(user_create_page)
pages.register_front_pages(user_edit_page)
