from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'extension_admin'
name = '插件管理'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑插件"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


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
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/extensions/',
        )
    },
    local_actions={
        # 加载/卸载 插件 TODO
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/extensions/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/extensions/{id}/"
        ),
    }
)


