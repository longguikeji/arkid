from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_list'
name = '应用列表'


page = pages.TabsPage(tag=tag, name=name)


appstore_page = pages.TabsPage(name=_("APP Store", "应用商店"))

private_app_page = pages.TabsPage(name=_("Private APP Store", "私有化应用商店"))


# store_page = pages.CardsPage(name=_("APP Store", "应用商店"))
store_page = pages.TreePage(name=_("APP Store", "应用商店"),show_vnode=True,show_page_if_no_node=False)
store_group_apps_page = pages.CardsPage(name='')


# app_purchased_page = pages.CardsPage(name=_("Purchased", "已购买"))
app_purchased_page = pages.TreePage(name=_("Purchased", "已购买"),show_vnode=True,show_page_if_no_node=False)
app_cascade_purchased_page = pages.CardsPage(name='')

order_page = pages.StepPage(name=_('Order', '购买'))
trial_page = pages.FormPage(name=_('Trial', '试用'))

installed_page = pages.TreePage(name=_("Local App", "本地应用"),show_vnode=True,show_page_if_no_node=False)
installed_cascade_page = pages.CardsPage(name='')

price_page = pages.CardsPage(name='选择价格')
copies_page = pages.FormPage(name='人天份数')
payment_page = pages.FormPage(name='支付')

private_appstore_page = pages.TreePage(name=_("Private APP Store", "私有化应用商店"),show_vnode=True,show_page_if_no_node=False)


pages.register_front_pages(page)
pages.register_front_pages(installed_page)
pages.register_front_pages(installed_cascade_page)
pages.register_front_pages(appstore_page)
pages.register_front_pages(store_page)
pages.register_front_pages(private_app_page)
pages.register_front_pages(private_appstore_page)
pages.register_front_pages(app_purchased_page)
pages.register_front_pages(app_cascade_purchased_page)
pages.register_front_pages(order_page)
pages.register_front_pages(trial_page)
pages.register_front_pages(price_page)
pages.register_front_pages(copies_page)
pages.register_front_pages(payment_page)
pages.register_front_pages(store_group_apps_page)


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

private_app_page.add_pages([
    installed_page,
    store_page,
    app_purchased_page
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
    # init_action=actions.DirectAction(
    #     path='/api/v1/tenant/{tenant_id}/apps/',
    #     method=actions.FrontActionMethod.GET,
    # ),
    # global_actions={
    #     'create':actions.CreateAction(
    #         path='/api/v1/tenant/{tenant_id}/apps/'
    #     ),
    #     "order_name":actions.OrderSetAction(
    #         path='/api/v1/tenant/{tenant_id}/apps/',
    #         method=actions.FrontActionMethod.GET,
    #         order_parms=["name"]
    #     )
    # },
    # node_actions=[
    #     actions.DirectAction(
    #         path='/api/v1/tenant/{tenant_id}/arkstore/apps/{id}/click/',
    #         method=actions.FrontActionMethod.GET,
    #     )
    # ],
    # local_actions={
    #     "config":actions.OpenAction(
    #         name = _("协议配置"),
    #         icon = "icon-edit",
    #         page=config_page,
    #     ),
    #     "openapi_version": actions.OpenAction(
    #         name = _("开放API配置"),
    #         page=openapi_page,
    #     ),
    #     "group": [
    #         actions.EditAction(
    #             page=edit_page,
    #         ),
    #         actions.DeleteAction(
    #             path="/api/v1/tenant/{tenant_id}/apps/{id}/",
    #         ),
    #     ]
    # },
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


store_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app&parent_id={id}',
            method=actions.FrontActionMethod.GET,
        ),
        actions.CascadeAction(
            page=store_group_apps_page
        )
    ]
    # init_action=actions.DirectAction(
    #     path='/api/v1/tenant/{tenant_id}/arkstore/apps/',
    #     method=actions.FrontActionMethod.GET
    # ),
    # local_actions={
    #     "order": actions.DirectAction(
    #         name='安装到本地',
    #         path='/api/v1/tenant/{tenant_id}/arkstore/install/{uuid}/',
    #         method=actions.FrontActionMethod.POST
    #     )
    # },
)

store_group_apps_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/apps/?category_id={category_id}',
        method=actions.FrontActionMethod.GET
    ),
    # node_actions=[
    #     actions.DirectAction(
    #         path='/api/v1/tenant/{tenant_id}/arkstore/apps/{id}/click/',
    #         method=actions.FrontActionMethod.GET,
    #     ),
    # ],
    local_actions={
        "order": actions.DirectAction(
            name='安装到本地',
            path='/api/v1/tenant/{tenant_id}/arkstore/install/{uuid}/',
            method=actions.FrontActionMethod.POST
        )
    },
    # global_actions={
    #     "order_name":actions.OrderAction(
    #         up="/api/v1/tenant/{tenant_id}/arkstore/apps/?category_id={category_id}",
    #         down="/api/v1/tenant/{tenant_id}/arkstore/apps/?category_id={category_id}",
    #         method=actions.FrontActionMethod.GET,
    #         order_parm="name"
    #     )
    # }
)

app_purchased_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app&parent_id={id}',
            method=actions.FrontActionMethod.GET,
        ),
        actions.CascadeAction(
            page=app_cascade_purchased_page
        )
    ]
    # init_action=actions.DirectAction(
    #     path='/api/v1/tenant/{tenant_id}/arkstore/purchased/apps/',
    #     method=actions.FrontActionMethod.GET
    # ),
    # local_actions={
    #     "order": actions.OpenAction(
    #         name='购买',
    #         page=order_page,
    #         show="can_buy"
    #     ),
    #     "trial": actions.OpenAction(
    #         name='试用',
    #         page=trial_page,
    #         show="can_try"
    #     )
    # },
)

app_cascade_purchased_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/purchased/apps/?category_id={category_id}',
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
