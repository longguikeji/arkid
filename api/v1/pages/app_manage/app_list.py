from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_list'
name = '应用列表'


page = pages.TabsPage(tag=tag, name=name)

edit_page = pages.FormPage(name=_("编辑应用"))
config_page = pages.FormPage(name=_("配置应用"))
openapi_page = pages.FormPage(name=_("开放API配置"))

installed_page = pages.TreePage(name=_("Local App", "本地应用"),show_vnode=True,show_page_if_no_node=False)
installed_cascade_page = pages.CardsPage(name='')

pages.register_front_pages(page)
pages.register_front_pages(installed_page)
pages.register_front_pages(installed_cascade_page)
pages.register_front_pages(edit_page)
pages.register_front_pages(config_page)
pages.register_front_pages(openapi_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='app_list',
    page=page,
)

page.add_pages([
    installed_page,
])

installed_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app&show_local=1',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app&show_local=1&parent_id={id}',
            method=actions.FrontActionMethod.GET,
        ),
        actions.CascadeAction(
            page=installed_cascade_page
        )
    ]
)

installed_cascade_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/?category_id={category_id}',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create':actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/apps/'
        ),
        "order_name":actions.OrderSetAction(
            path='/api/v1/tenant/{tenant_id}/apps/',
            method=actions.FrontActionMethod.GET,
            order_parms=["name"]
        )
    },
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/arkstore/apps/{id}/click/',
            method=actions.FrontActionMethod.GET,
        )
    ],
    local_actions={
        "config":actions.OpenAction(
            name = _("协议配置"),
            icon = "icon-edit",
            page=config_page,
        ),
        "openapi_version": actions.OpenAction(
            name = _("开放API配置"),
            page=openapi_page,
        ),
        "group": [
            actions.EditAction(
                page=edit_page,
            ),
            actions.DeleteAction(
                path="/api/v1/tenant/{tenant_id}/apps/{id}/",
            ),
        ]
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/"
        ),
    }
)

openapi_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{app_id}/openapi_version/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{app_id}/openapi_version/"
        ),
    }
)

config_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/config/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/config/"
        ),
    }
)
