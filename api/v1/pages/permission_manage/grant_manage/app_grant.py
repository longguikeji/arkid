from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_grant'
name = '所有应用'


page = pages.TreePage(tag=tag,name=name)
app_permission_page = pages.TablePage(name=_("该应用权限"))
update_app_permission_page = pages.TablePage(name=_("更新应用权限"), select=True)

pages.register_front_pages(page)
pages.register_front_pages(app_permission_page)
pages.register_front_pages(update_app_permission_page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/all_apps_in_arkid/?not_arkid=1',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=app_permission_page
        )
    ]
)

app_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/permissions',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "delete": actions.DeleteAction(
            path='/api/v1/tenant/{tenant_id}/permission/app/{select_app_id}/{permission_id}/remove_permission'
        )
    },
    global_actions={
        'open': actions.OpenAction(
            name=("添加应用权限"),
            page=update_app_permission_page
        ),
    }
)

update_app_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permissions',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'confirm':actions.ConfirmAction(
            path='/api/v1/tenant/{tenant_id}/permission/app/{select_app_id}/add_permission',
        ),
    }
)