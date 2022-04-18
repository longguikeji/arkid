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
    type=pages.TABLE_PAGE_TYPE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method='get'
    )
)

user_edit_page = pages.FrontPage(
    tag="user.edit",
    name=_("编辑用户"),
    type=pages.FORM_PAGE_TYPE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/{id}/',
        method='get'
    )
)

user_edit_page.add_global_action(
    [
        pages.FrontAction(
            tag="user.edit",
            method="post",
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/users/{id}/"
        ),
        
    ]
)

user_create_page = pages.FrontPage(
    tag="user.create",
    name=_("创建用户"),
    type=pages.FORM_PAGE_TYPE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method='post'
    )
)

user_create_page.add_global_action(
    [
        pages.FrontAction(
            tag="user.create",
            method="post",
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/users/"
        )
    ]
)

page.add_local_action(
    [
        pages.FrontAction(
            name=_("编辑用户"),
            page=user_edit_page,
            icon="el-icon-update"
        ),
        pages.FrontAction(
            name=_("删除用户"),
            method="delete",
            path="/api/v1/tenant/{tenant_id}/users/{id}/",
            icon="el-icon-delete"
        )
    ]
)

page.add_global_action(
    [
        pages.FrontAction(
            name="创建用户",
            page=user_create_page,
            icon="el-icon-plus"
        )
    ]
)

pages.register_front_pages(page)
