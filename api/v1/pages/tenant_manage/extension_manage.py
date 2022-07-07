# 租户下的 extension的settings  config 
from platform import platform
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _
from ..platform_admin.extension_admin import markdown_page

tag = 'tenant_extension_manage'
name = '插件管理'


page = pages.TabsPage(tag=tag, name=name)
platform_extension_page = pages.CardsPage(name=_('Platform Extensions', '插件租赁'))
tenant_extension_rented_page = pages.CardsPage(name=_('Rented Extensions', '已租赁'))
rent_page = pages.StepPage(name=_('Rent', '租赁'))
setting_page = pages.FormPage(name='插件租户配置')
config_page = pages.TablePage(name='插件运行时配置')
create_config_page = pages.FormPage(name='创建插件运行时配置')
update_config_page = pages.FormPage(name='更新插件运行时配置')
price_page = pages.CardsPage(name='选择价格')
copies_page = pages.FormPage(name='人天份数')
payment_page = pages.FormPage(name='支付')


pages.register_front_pages(page)
pages.register_front_pages(platform_extension_page)
pages.register_front_pages(tenant_extension_rented_page)
pages.register_front_pages(rent_page)
pages.register_front_pages(setting_page)
pages.register_front_pages(config_page)
pages.register_front_pages(create_config_page)
pages.register_front_pages(update_config_page)
pages.register_front_pages(price_page)
pages.register_front_pages(copies_page)
pages.register_front_pages(payment_page)


page.add_pages([
    tenant_extension_rented_page,
    platform_extension_page
])

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)

platform_extension_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/platform/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "markdown": actions.OpenAction(
            name='文档',
            page=markdown_page  
        ),
        "rent": actions.OpenAction(
            name="租赁",
            page=rent_page
        )
    },
)

rent_page.add_pages([
    price_page,
    copies_page,
    payment_page
])

price_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/rent/extensions/{package}/',
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
            path="/api/v1/tenant/{tenant_id}/arkstore/rent/extensions/{package}/",
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
            path="/api/v1/tenant/{tenant_id}/arkstore/rent/order/{order_no}/payment_status/extensions/{package}/",
            method=actions.FrontActionMethod.GET
        ),
    }
)

tenant_extension_rented_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/tenant/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "active": actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/tenant/extensions/{id}/active/',
            method=actions.FrontActionMethod.POST,
        ),
        "markdown": actions.OpenAction(
            name='文档',
            page=markdown_page  
        ),
        "setting": actions.OpenAction(
            name='租户配置',
            page=setting_page
        ),
        "config": actions.OpenAction(
            name='运行时配置',
            page=config_page
        ),
    },
)

setting_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/extension/{extension_id}/settings/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/extension/{extension_id}/settings/"
        ),
    }
)

config_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'new': actions.CreateAction(
            path="/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/",
            init_data={
                'package': 'package'
            }
        ),
    },
    local_actions={
        "update": actions.OpenAction(
            name='更新',
            page=update_config_page
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/{config_id}/",
        )
    }
)


update_config_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/{config_id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/{config_id}/"
        ),
    }
)