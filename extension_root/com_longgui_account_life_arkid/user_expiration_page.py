#!/usr/bin/env python3

from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _


tag = 'user_expiration_setting'
name = '用户过期设置'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑用户过期设置"))


# pages.register_front_pages(page)
# pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='settings',
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/account_life_arkid/user_expiration/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/account_life_arkid/user_expiration/',
        )
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}/",
        ),
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}/"
        ),
    },
)
