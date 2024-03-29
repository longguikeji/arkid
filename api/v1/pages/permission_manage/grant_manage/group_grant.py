from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'group_grant'
name = '所有分组'


page = pages.TreePage(tag=tag,name=name)
group_permission_page = pages.TablePage(name=_("该分组权限"))
update_group_permission_page = pages.TablePage(name=_("更新用户分组权限"),select=True)
show_group_permission_page = pages.TreePage(name=_("查看用户分组最终权限"))
user_group_permission_page = pages.TablePage(name=_("该用户分组的应用权限"))

pages.register_front_pages(page)
pages.register_front_pages(group_permission_page)
pages.register_front_pages(update_group_permission_page)
pages.register_front_pages(show_group_permission_page)
pages.register_front_pages(user_group_permission_page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/user_groups/?parent_id={id}',
            method=actions.FrontActionMethod.GET
        ),
        actions.CascadeAction(
            page=group_permission_page
        )
    ],
)

group_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/group_permissions?select_usergroup_id={select_usergroup_id}',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "delete": actions.DeleteAction(
            path='/api/v1/tenant/{tenant_id}/permission/usergroup/{select_usergroup_id}/{permission_id}/remove_permission'
        )
    },
    global_actions={
        'open': actions.OpenAction(
            name=("添加用户分组权限"),
            page=update_group_permission_page
        ),
        'show': actions.OpenAction(
            name=("查看最终权限"),
            page=show_group_permission_page
        )
    }
)
show_group_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/all_apps_in_arkid/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=user_group_permission_page
        )
    ]
)
user_group_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_group_last_permissions?usergroup_id={usergroup_id}&app_id={app_id}',
        method=actions.FrontActionMethod.GET
    ),
)

update_group_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permissions',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'confirm':actions.ConfirmAction(
            path='/api/v1/tenant/{tenant_id}/permission/usergroup/{select_usergroup_id}/add_permission',
        ),
    }
)