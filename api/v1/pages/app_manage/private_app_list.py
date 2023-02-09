from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'private_app'
name = '私有化应用'


page = pages.TabsPage(tag=tag, name=name)

store_page = pages.TreePage(name=_("Private App Store", "私有化应用商店"),show_vnode=True,show_page_if_no_node=False)
store_cascade_page = pages.CardsPage(name='')

# installed_page = pages.TreePage(name=_("Installed", "已安装"),show_vnode=True,show_page_if_no_node=False)
# installed_cascade_page = pages.CardsPage(name='')

default_values_page = pages.FormPage(name=_("默认配置"))
order_page = pages.StepPage(name=_('Order', '购买'))
trial_page = pages.FormPage(name=_('Trial', '试用'))

purchased_page = pages.TreePage(name=_("Purchased", "已购买"),show_vnode=True,show_page_if_no_node=False)
purchased_cascade_page = pages.CardsPage(name='')

price_page = pages.CardsPage(name='选择价格')
copies_page = pages.FormPage(name='人天份数')
payment_page = pages.FormPage(name='支付')

install_page = pages.FormPage(name=_("安装"))


pages.register_front_pages(page)
# pages.register_front_pages(installed_page)
# pages.register_front_pages(installed_cascade_page)
pages.register_front_pages(store_page)
pages.register_front_pages(store_cascade_page)
pages.register_front_pages(default_values_page)
pages.register_front_pages(order_page)
pages.register_front_pages(trial_page)
pages.register_front_pages(purchased_page)
pages.register_front_pages(purchased_cascade_page)
pages.register_front_pages(price_page)
pages.register_front_pages(copies_page)
pages.register_front_pages(payment_page)
pages.register_front_pages(install_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='extension',
)

page.add_pages([
    # installed_page,
    store_page,
    purchased_page
])

# installed_page.create_actions(

#     init_action=actions.DirectAction(
#         path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app',
#         method=actions.FrontActionMethod.GET,
#     ),
#     node_actions=[
#         actions.DirectAction(
#             path='/api/v1/tenant/{tenant_id}/arkstore/categorys/?type=app&parent_id={id}',
#             method=actions.FrontActionMethod.GET,
#         ),
#         actions.CascadeAction(
#             page=installed_cascade_page
#         )
#     ]
# )
# installed_cascade_page.create_actions(
#     init_action=actions.DirectAction(
#         path='/api/v1/extensions/?category_id={category_id}',
#         method=actions.FrontActionMethod.GET,
#     ),
# )


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
            page=store_cascade_page
        )
    ]
)
store_cascade_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/private_apps/?category_id={category_id}',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "order": actions.OpenAction(
            name='购买',
            page=order_page
        ),
        "trial": actions.OpenAction(
            name='试用',
            page=trial_page
        )
    },
)

purchased_page.create_actions(

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
            page=purchased_cascade_page
        )
    ]
)
purchased_cascade_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/purchased/private_apps/?category_id={category_id}',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "config": actions.OpenAction(
            name='默认配置',
            page=default_values_page
        ),
        "install": actions.OpenAction(
            name='安装/更新',
            page=install_page
        ),
    },
)


default_values_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/private_app/{uuid}/default_values/',
        method=actions.FrontActionMethod.GET
    )
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

install_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/install/private_app/{uuid}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "confirm": actions.DirectAction(
            name='安装/更新',
            path='/api/v1/tenant/{tenant_id}/arkstore/install/private_app/{uuid}/',
            method=actions.FrontActionMethod.POST
        ),
    },
)