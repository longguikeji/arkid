from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_list'
name = '应用列表'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑应用"))
config_page = pages.FormPage(name=_("配置应用"))

pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(config_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='app',
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create':actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/apps/'
        )
    },
    local_actions={
        "config":actions.OpenAction(
            name = _("配置"),
            icon = "icon-edit",
            page=config_page,
        ),
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/"
        ),
    }
)

config_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/config/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/config/"
        ),
    }
)