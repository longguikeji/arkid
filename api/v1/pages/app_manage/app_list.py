from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_list'
name = '应用列表'


page = pages.TabsPage(tag=tag, name=name)

edit_page = pages.FormPage(name=_("编辑应用"))
config_page = pages.FormPage(name=_("配置应用"))
openapi_page = pages.FormPage(name=_("开放API配置"))
appstore_page = pages.TabsPage(name=_("APP Store", "应用商店"))
store_page = pages.CardsPage(name=_("APP Store", "应用商店"))
app_purchased_page = pages.CardsPage(name=_("Purchased", "已安装"))
order_page = pages.StepPage(name=_('Order', '购买'))
trial_page = pages.FormPage(name=_('Trial', '试用'))
installed_page = pages.CardsPage(name='本地应用')
price_page = pages.CardsPage(name='选择价格')
copies_page = pages.FormPage(name='人天份数')
payment_page = pages.FormPage(name='支付')

pages.register_front_pages(page)
pages.register_front_pages(installed_page)
pages.register_front_pages(edit_page)
pages.register_front_pages(config_page)
pages.register_front_pages(openapi_page)
pages.register_front_pages(appstore_page)
pages.register_front_pages(store_page)
pages.register_front_pages(app_purchased_page)
pages.register_front_pages(order_page)
pages.register_front_pages(trial_page)
pages.register_front_pages(price_page)
pages.register_front_pages(copies_page)
pages.register_front_pages(payment_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='list',
    page=page,
)

page.add_pages([
    installed_page,
    store_page,
    app_purchased_page
])

installed_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create':actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/apps/'
        ),
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

store_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/apps/',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "order": actions.DirectAction(
            name='安装到本地',
            path='/api/v1/tenant/{tenant_id}/arkstore/install/{uuid}/',
            method=actions.FrontActionMethod.POST
        )
    },
)

app_purchased_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/purchased/apps/',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "order": actions.OpenAction(
            name='购买',
            page=order_page,
            show="can_buy"
        ),
        "trial": actions.OpenAction(
            name='试用',
            page=trial_page,
            show="can_try"
        )
    },
)

order_page.add_pages([
    price_page,
    copies_page,
    payment_page
])

price_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
       'next': actions.NextAction(
            name="选择价格"
        ),
    }
)

copies_page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/set_copies/",
        method=actions.FrontActionMethod.POST
    ),
    global_actions={
       'next': actions.NextAction(
            name="创建订单",
            path="/api/v1/tenant/{tenant_id}/arkstore/order/extensions/{uuid}/",
            method=actions.FrontActionMethod.POST
        ),
    }
)

payment_page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/arkstore/order/{order_no}/payment/",
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'next': actions.NextAction(
            name="已支付",
            path="/api/v1/tenant/{tenant_id}/arkstore/purchase/order/{order_no}/payment_status/",
            method=actions.FrontActionMethod.GET
        ),
    }
)

trial_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/trial/extensions/{uuid}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "confirm": actions.DirectAction(
            name='试用',
            path='/api/v1/tenant/{tenant_id}/arkstore/trial/extensions/{uuid}/',
            method=actions.FrontActionMethod.POST
        ),
    },
)
