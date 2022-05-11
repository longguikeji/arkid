from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'scim_sync'
name = 'SCIM数据同步'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑用户/群组数据同步配置"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/scim_syncs/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/scim_syncs/',
        )
    },
    local_actions={
        "direct": actions.DirectAction(
            name=_("同步"),
            method=actions.FrontActionMethod.GET,
            path="/api/v1/tenant/{tenant_id}/scim_syncs/{id}/sync/",
        ),
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/scim_syncs/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/scim_syncs/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/scim_syncs/{id}/"
        ),
    }
)


