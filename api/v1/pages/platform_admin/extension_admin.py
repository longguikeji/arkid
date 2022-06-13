from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'extension_admin'
name = '插件商店'


page = pages.TabsPage(tag=tag, name=name)
store_page = pages.TablePage(name='插件商店')
order_page = pages.FormPage(name=_('Order', '购买'))
bind_agent_page = pages.FormPage(name=_('Bind Agent', '绑定代理商'))
purchased_page = pages.TablePage(name='已购买')
download_page = pages.TablePage(name='已安装')
edit_page = pages.FormPage(name=_("编辑插件"))


pages.register_front_pages(page)
pages.register_front_pages(store_page)
pages.register_front_pages(order_page)
pages.register_front_pages(bind_agent_page)
pages.register_front_pages(purchased_page)
pages.register_front_pages(download_page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='extension',
)

page.add_pages([
    store_page,
    purchased_page,
    download_page
])

store_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
       'bind_agent': actions.OpenAction(
            name='绑定代理商',
            page=bind_agent_page
        ),
    },
    local_actions={
        "order": actions.OpenAction(
            name='购买',
            page=order_page
        )
    },
)

purchased_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/purchased/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "install": actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/arkstore/install/{uuid}/',
            method=actions.FrontActionMethod.POST,
        ),
    },
)

download_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "update": actions.DirectAction(
            name='更新',
            path='/api/v1/tenant/{tenant_id}/arkstore/install/{uuid}/',
            method=actions.FrontActionMethod.POST,
        ),
        "active": actions.DirectAction(
            name='切换启用状态',
            path='/api/v1/extensions/{id}/active/',
            method=actions.FrontActionMethod.POST,
        ),
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/extensions/{id}/"
        ),
    }
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


bind_agent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/bind_agent/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "confirm": actions.DirectAction(
            name='修改',
            path='/api/v1/tenant/{tenant_id}/arkstore/bind_agent/',
            method=actions.FrontActionMethod.PUT
        ),
        "delete": actions.DirectAction(
            name='删除',
            path='/api/v1/tenant/{tenant_id}/arkstore/bind_agent/',
            method=actions.FrontActionMethod.DELETE
        ),
    },
)
