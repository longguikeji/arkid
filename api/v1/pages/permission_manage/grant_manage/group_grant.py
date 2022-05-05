from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'group_grant'
name = '所有分组'


page = pages.ListPage(tag=tag,name=name)
group_permission_page = pages.TablePage(name=_("该分组权限"))
update_group_permission_page = pages.TablePage(name=_("更新用户分组权限"),select=True)

pages.register_front_pages(page)
pages.register_front_pages(group_permission_page)
pages.register_front_pages(update_group_permission_page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=group_permission_page
        )
    ],
)

group_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "delete": actions.DeleteAction(
            path='/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/{id}/'
        )
    },
    global_actions={
        'open': actions.OpenAction(
            name=("添加用户分组权限"),
            page=update_group_permission_page
        )
    }
)

update_group_permission_page.create_actions(
    init_action=actions.DeleteAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/all_permissions/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'confirm':actions.ConfirmAction(
            path='/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/',
        ),
    }
)