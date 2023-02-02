#!/usr/bin/env python3

from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _
from arkid.core.extension import create_extension_page

tag = 'default_approve_requests'
name = '默认请求处理'


router_page = create_extension_page(__file__, pages.TabsPage, tag=tag, name=name)
waiting_page = create_extension_page(__file__, pages.TablePage, name='未审核')
approved_page = create_extension_page(__file__, pages.TablePage, name='已审核')


router_page.add_pages(
    [
        waiting_page,
        approved_page,
    ]
)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=router_page,
    icon='default_approve_requests',
)

package = 'com.longgui.approve.system.arkid'.replace('.', '_')

waiting_page.create_actions(
    init_action=actions.DirectAction(
        path=f'/api/v1/tenant/{{tenant_id}}/{package}/approve_requests/?is_approved=false',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "pass": actions.DirectAction(
            name=_("Pass", "通过"),
            path=f"/api/v1/{package}/approve_requests/{{request_id}}/pass/",
            method=actions.FrontActionMethod.PUT,
        ),
        "deny": actions.DirectAction(
            name=_("Deny", "拒绝"),
            path=f"/api/v1/{package}/approve_requests/{{request_id}}/deny/",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)

approved_page.create_actions(
    init_action=actions.DirectAction(
        path=f'/api/v1/tenant/{{tenant_id}}/{package}/approve_requests/?is_approved=true',
        method=actions.FrontActionMethod.GET,
    ),
    # local_actions={
    #     "pass": actions.DirectAction(
    #         name=_("Pass", "通过"),
    #         path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=pass",
    #         method=actions.FrontActionMethod.PUT,
    #     ),
    #     "deny": actions.DirectAction(
    #         name=_("Deny", "拒绝"),
    #         path="/api/v1/tenant/{tenant_id}/approve_requests/arkid/{id}/?action=deny",
    #         method=actions.FrontActionMethod.PUT,
    #     ),
    # },
)
