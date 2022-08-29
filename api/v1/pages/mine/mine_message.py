from mimetypes import init
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'mine_message'
name = '我的消息'

page = pages.TreePage(tag = tag, name = name)
mine_message_page = pages.TablePage(
    name="消息记录"
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
        path='/api/v1/mine/message_senders/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=mine_message_page
        )
    ],
)

mine_message_page.create_actions(
    init_action = actions.DirectAction(
        path='/api/v1/mine/sender_messages/{id}/',
        method=actions.FrontActionMethod.GET,
    )
)