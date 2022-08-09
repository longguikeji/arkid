# 租户下的 extension的settings  config 
from select import select
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'front_theme'
name = '主题设置'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑主题"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='theme',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/front_theme_list/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create':actions.CreateAction(
            name='添加主题',
            path='/api/v1/tenant/{tenant_id}/front_theme/',
        )
    },
    local_actions={
        'edit':actions.EditAction(
            page=edit_page,
        ),
        'delete':actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/front_theme/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/front_theme/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'confirm':actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/front_theme/{id}/"),
    }
)


