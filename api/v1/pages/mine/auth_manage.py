from arkid.core.translation import gettext_default as _
from arkid.core import routers,pages,actions
from arkid.core.pages import TabsPage

tag = "mine_auth_manage"
name = _("认证管理")

mine_accounts_bind_page = pages.TablePage(name='三方账号绑定')
mine_accounts_unbind_page = pages.TablePage(name='三方账号解绑')

mine_accounts_bind_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/unbind_accounts/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "unbind": actions.DirectAction(
            name='绑定',
            path='/api/v1/mine/tenant/{tenant_id}/accounts/{account_id}/bind',
            method=actions.FrontActionMethod.GET,
        ),
    },
)

mine_accounts_unbind_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/accounts/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "unbind": actions.DirectAction(
            name='解绑',
            path='/api/v1/mine/tenant/{tenant_id}/accounts/{account_id}/unbind',
            method=actions.FrontActionMethod.GET,
        ),
    },
)

page = TabsPage(
    name=name,
    tag=tag
)

pages.register_front_pages(page)
pages.register_front_pages(mine_accounts_bind_page)
pages.register_front_pages(mine_accounts_unbind_page)

page.add_pages([
    mine_accounts_bind_page,
    mine_accounts_unbind_page
])

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='auth',
    page=page
)