from arkid.core.translation import gettext_default as _
from arkid.core import routers, pages, actions

tag = 'user_log'
name = '用户行为日志'

page = pages.TablePage(tag = tag, name = name)
detail_page = pages.DescriptionPage(name=_("日志详情"))

# pages.register_front_pages(page)
# pages.register_front_pages(detail_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='user_log',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_logging_mysql/user_log/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "open": actions.OpenAction(
            name=_("查阅"),
            page=detail_page
        )
    }
)

detail_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_logging_mysql/log/{id}/',
        method=actions.FrontActionMethod.GET,
    )
)