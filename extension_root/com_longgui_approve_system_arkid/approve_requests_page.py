#!/usr/bin/env python3

from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'arkid_approve_requests'
name = '审批请求-ArkID'


page = pages.TablePage(tag=tag, name=name)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/approve_system_arkid/approve_requests/?package=com.longgui.approve.system.arkid',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "pass": actions.DirectAction(
            path="/api/v1/tenant/{tenant_id}/approve_system_arkid/approve_requests/{id}/?action=pass",
            method=actions.FrontActionMethod.PUT,
        ),
        "deny": actions.DirectAction(
            path="/api/v1/tenant/{tenant_id}/approve_system_arkid/approve_requests/{id}/?action=pass",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)
