#!/usr/bin/env python3

from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'default_approve_requests'
name = '默认请求处理'


page = pages.TabsPage(tag=tag, name=name)
waiting_page = pages.TablePage(name='未审核')
approved_page = pages.TablePage(name='已审核')

pages.register_front_pages(page)
pages.register_front_pages(waiting_page)
pages.register_front_pages(approved_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.add_pages(
    [
        waiting_page,
        approved_page,
    ]
)

waiting_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/approve_requests/arkid/?is_approved=false',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "pass": actions.DirectAction(
            name=_("Pass", "通过"),
            path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=pass",
            method=actions.FrontActionMethod.PUT,
        ),
        "deny": actions.DirectAction(
            name=_("Deny", "拒绝"),
            path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=deny",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)

approved_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/approve_requests/arkid/?is_approved=true',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "pass": actions.DirectAction(
            name=_("Pass", "通过"),
            path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=pass",
            method=actions.FrontActionMethod.PUT,
        ),
        "deny": actions.DirectAction(
            name=_("Deny", "拒绝"),
            path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=deny",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)
