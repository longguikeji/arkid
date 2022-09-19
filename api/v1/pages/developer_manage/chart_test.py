from arkid.core import actions, pages
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _

tag = "chart_test"
name = _("图表测试")

page = pages.ChartPage(tag=tag,name=name)

pages.register_front_pages(page)

router = FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/test_chart/',
        method=actions.FrontActionMethod.GET,
    ),
)