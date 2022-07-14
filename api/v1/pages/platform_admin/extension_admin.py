from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'extension_admin'
name = '平台插件'


page = pages.TabsPage(tag=tag, name=name)

store_page = pages.CardsPage(name='插件商店')
installed_page = pages.CardsPage(name='已安装')
arkstore_markdown_page = pages.FormPage(name=_("文档"))
order_page = pages.StepPage(name=_('Order', '购买'))
trial_page = pages.FormPage(name=_('Trial', '试用'))
bind_agent_page = pages.FormPage(name=_('Bind Agent', '绑定代理商'))
purchased_page = pages.CardsPage(name='已购买')
markdown_page = pages.FormPage(name=_("文档"))
profile_page = pages.FormPage(name='插件配置')
price_page = pages.CardsPage(name='选择价格')
copies_page = pages.FormPage(name='人天份数')
payment_page = pages.FormPage(name='支付')


pages.register_front_pages(page)
pages.register_front_pages(installed_page)
pages.register_front_pages(store_page)
pages.register_front_pages(arkstore_markdown_page)
pages.register_front_pages(order_page)
pages.register_front_pages(trial_page)
pages.register_front_pages(bind_agent_page)
pages.register_front_pages(purchased_page)
pages.register_front_pages(markdown_page)
pages.register_front_pages(profile_page)
pages.register_front_pages(price_page)
pages.register_front_pages(copies_page)
pages.register_front_pages(payment_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='extension',
)

page.add_pages([
    installed_page,
    store_page,
    purchased_page
])

installed_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "markdown": actions.OpenAction(
            name='文档',
            page=markdown_page
        ),
        "update": actions.DirectAction(
            name='更新',
            path='/api/v1/tenant/{tenant_id}/arkstore/update/{package}/',
            method=actions.FrontActionMethod.POST,
        ),
        "active": actions.DirectAction(
            name='切换启用状态',
            path='/api/v1/extensions/{id}/active/',
            method=actions.FrontActionMethod.POST,
        ),
        "profile": actions.OpenAction(
            name='插件配置',
            page=profile_page
        ),
    },
)

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
        "markdown": actions.OpenAction(
            name='文档',
            page=arkstore_markdown_page
        ),
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
        path='/api/v1/tenant/{tenant_id}/arkstore/purchased/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "install": actions.DirectAction(
            name='安装',
            path='/api/v1/tenant/{tenant_id}/arkstore/install/{uuid}/',
            method=actions.FrontActionMethod.POST,
        ),
    },
)

markdown_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/{id}/markdown/',
        method=actions.FrontActionMethod.GET
    )
)

arkstore_markdown_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/extensions/{uuid}/markdown/',
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

profile_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/{id}/profile/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/extensions/{id}/profile/"
        ),
    }
)

bind_agent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/bind_agent/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "confirm": actions.DirectAction(
            name='确定',
            path='/api/v1/tenant/{tenant_id}/arkstore/bind_agent/',
            method=actions.FrontActionMethod.PUT
        ),
        # "delete": actions.DirectAction(
        #     name='删除',
        #     path='/api/v1/tenant/{tenant_id}/arkstore/bind_agent/',
        #     method=actions.FrontActionMethod.DELETE
        # ),
    },
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