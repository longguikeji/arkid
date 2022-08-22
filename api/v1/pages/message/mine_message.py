from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'mine_message'
name = '我的消息'

page = pages.TablePage(tag = tag, name = name)
mine_message_page = pages.FormPage(
    name="消息详情"
)

pages.register_front_pages(page)
pages.register_front_pages(mine_message_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='message',
)

page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/mine/messages/",
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "edit": actions.DirectAction(
            page=mine_message_page
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/mine/messages/{id}/",
        )
    },
)

mine_message_page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/mine/messages/{id}/",
        method=actions.FrontActionMethod.GET
    )
)