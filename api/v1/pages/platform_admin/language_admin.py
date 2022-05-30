from arkid.core.translation import gettext_default as _
from arkid.core import routers, pages, actions

tag = 'language_admin'
name = '语言包管理'

page = pages.TablePage(tag = tag, name = name)
edit_page = pages.TablePage(name=_("编辑语言包"))

pages.register_front_pages(page)
pages.register_front_pages(edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='language',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/languages/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/languages/',
        )
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/languages/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/languages/{id}/translates/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'add': actions.OpenAction(
            name = "新增",
            icon = "icon-create",
            method = actions.FrontActionMethod.POST,
            path='/api/v1/tenant/{tenant_id}/languages/{id}/translates/',
        ),
    }
)
