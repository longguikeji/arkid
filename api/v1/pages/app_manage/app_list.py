from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_list'
name = '应用列表'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑应用"))
config_page = pages.FormPage(name=_("配置应用"))
appstore_page = pages.TabsPage(name=_("APP Store", "应用商店"))
app_list_page = pages.TablePage(name=_("APP Store", "应用商店"))
app_purchased_page = pages.TablePage(name=_("Purchased", "已购买"))
order_page = pages.FormPage(name=_('Order', '购买'))

pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(config_page)
pages.register_front_pages(appstore_page)
pages.register_front_pages(app_list_page)
pages.register_front_pages(app_purchased_page)
pages.register_front_pages(order_page)

appstore_page.add_pages([
    app_list_page,
    app_purchased_page
])

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='list',
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create':actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/apps/'
        ),
        'appstore':actions.OpenAction(
            name='应用商店',
            page=appstore_page
        )
    },
    local_actions={
        "config":actions.OpenAction(
            name = _("协议配置"),
            icon = "icon-edit",
            page=config_page,
        ),
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/",
        )
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

app_list_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/apps/',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "order": actions.OpenAction(
            name='购买',
            page=order_page
        )
    },
)

app_purchased_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/purchased/apps/',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "install": actions.DirectAction(
            path="/api/v1/tenant/{tenant_id}/install/{uuid}/",
            method=actions.FrontActionMethod.POST
        )
    },
)

order_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "payed": actions.DirectAction(
            name='已支付',
            path='/api/v1/tenant/{tenant_id}/arkstore/order/status/extensions/{uuid}/',
            method=actions.FrontActionMethod.GET
        ),
    },
)
