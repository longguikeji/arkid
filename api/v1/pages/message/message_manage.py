from arkid.core import routers, pages, actions

tag = 'message_manage'
name = '消息管理'

page = pages.TablePage(tag = tag, name = name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='message',
)

page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/message/",
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/message/',
        )
    }
)