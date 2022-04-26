from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_group'
name = '应用分组'


page = pages.TreePage(tag=tag,name=name)
group_apps_page = pages.TablePage(name=_("组内应用"))
edit_apps_page = pages.TablePage(name=_("更新组内应用"))
create_page = pages.FormPage(name=_("创建应用分组"))
edit_page = pages.FormPage(name=_("编辑应用分组"))


pages.register_front_pages(page)
pages.register_front_pages(group_apps_page)
pages.register_front_pages(edit_apps_page)
pages.register_front_pages(create_page)
pages.register_front_pages(edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            page=create_page,
        )
    ],
    local_actions=[
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/app_groups/{id}/",
        )
    ],
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/app_groups/{app_group_id}/apps/',
            method=actions.FrontActionMethod.GET,
            result_page=group_apps_page
        )
    ]
)

group_apps_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/{app_group_id}/apps/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.OpenAction(
            name=_("添加应用"),
            page=edit_apps_page,
        )
    ],
    local_actions=[
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/app_groups/{app_group_id}/apps/{id}/",
            icon="icon-delete",
        )
    ],
)


edit_apps_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/{app_group_id}/select_apps/',
        method=actions.FrontActionMethod.GET,
    ),
    select=True,
    global_actions=[
        actions.ConfirmAction(
            path="/tenant/{tenant_id}/app_groups/{app_group_id}/apps/"
        ),
        actions.CancelAction()
    ]
)


edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/app_groups/{id}/"),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)

create_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/',
        method=actions.FrontActionMethod.POST
    ),
    global_actions=[
        actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/app_groups/",
        ),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)
