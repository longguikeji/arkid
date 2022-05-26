#!/usr/bin/env python3

from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'default_approve_requests'
name = '默认请求处理'


page = pages.TablePage(tag=tag, name=name)
pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/approve_requests/arkid/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "pass": actions.DirectAction(
            name="通过",
            path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=pass",
            method=actions.FrontActionMethod.PUT,
        ),
        "deny": actions.DirectAction(
            name="拒绝",
            path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=deny",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)
