# 租户下的 extension的settings  config 
from platform import platform
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'tenant_extension_manage'
name = '插件管理'


page = pages.TabsPage(tag=tag, name=name)
platform_extension_page = pages.TablePage(name=_('Platform Extensions', '平台插件'))
tenant_extension_rented_page = pages.TablePage(name=_('Rented Extensions', '已租赁'))
rent_page = pages.FormPage(name=_('Rent', '租赁'))


pages.register_front_pages(page)
pages.register_front_pages(platform_extension_page)
pages.register_front_pages(tenant_extension_rented_page)
pages.register_front_pages(rent_page)

page.add_pages([
    platform_extension_page,
    tenant_extension_rented_page
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
        "rent": actions.OpenAction(
            name="租赁",
            page=rent_page
        )
    },
)

rent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/arkstore/rent/extensions/{uuid}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "payed": actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/arkstore/rent/status/extensions/{uuid}/',
            method=actions.FrontActionMethod.GET,
        ),
    },
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
    },
)

