#!/usr/bin/env python3

from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'all_approve_requests'
name = '审批请求'


page = pages.TablePage(tag=tag, name=name)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='request',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/approve_requests/',
        method=actions.FrontActionMethod.GET,
    ),
)
