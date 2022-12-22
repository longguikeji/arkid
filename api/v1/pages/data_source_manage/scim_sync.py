from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'scim_sync'
name = 'SCIM数据同步'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑用户/群组数据同步配置"))
log_page = pages.TablePage(tag="scim_sync_log", name=_("同步日志"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(log_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='scim_sync',
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
        # "direct": actions.DirectAction(
        #     name=_("同步"),
        #     method=actions.FrontActionMethod.GET,
        #     path="/api/v1/tenant/{tenant_id}/scim_syncs/{id}/sync/",
        # ),
        "open": actions.OpenAction(
            name=_("同步日志"),
            page=log_page,
            icon="icon-edit",
        ),
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/scim_syncs/{id}/",
        ),
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/scim_syncs/{id}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/scim_syncs/{id}/",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)

log_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/scim_syncs/{id}/logs/',
        method=actions.FrontActionMethod.GET,
    ),
    # local_actions={
    #     "delete": actions.DeleteAction(
    #         path='/api/v1/tenant/{tenant_id}/scim_syncs/{id}/logs/{id}/',
    #     ),
    # },
    global_actions={
        'delete': actions.DeleteAction(
            name='清除日志',
            path='/api/v1/tenant/{tenant_id}/scim_syncs/{id}/logs/',
            method=actions.FrontActionMethod.DELETE,
        )
    },
)
