from arkid.core.translation import gettext_default as _
from arkid.core import routers, pages, actions

tag = 'language_admin'
name = '语言包管理'

page = pages.TablePage(tag = tag, name = name)
detail_page = pages.DescriptionPage(name=_("语言包详情"))

pages.register_front_pages(page)
pages.register_front_pages(detail_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/languages/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions=[
        actions.OpenAction(
            name=_("查阅"),
            page=detail_page
        )
    ]
)

detail_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/languages/',
        method=actions.FrontActionMethod.GET,
    )
)