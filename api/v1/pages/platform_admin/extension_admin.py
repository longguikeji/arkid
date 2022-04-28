from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'extension_admin'
name = '插件管理'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑插件"))
create_page = pages.FormPage(name=_("创建一个新的插件"))

pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(create_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            page=create_page,
        )
    ],
    local_actions=[
        # 加载/卸载 插件 TODO
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/extensions/{id}/",
        )
    ],
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/extensions/{id}/"),

    ]
)

create_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/',
        method=actions.FrontActionMethod.POST
    ),
    global_actions=[
        actions.ConfirmAction(
            path="/api/v1/extensions/",
        ),

    ]
)
