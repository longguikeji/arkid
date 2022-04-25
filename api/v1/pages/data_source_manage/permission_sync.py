# 权限数据同步
from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

permission_sync_tag = 'permission_sync'
permission_sync_name = '权限数据同步'


page = pages.TablePage(
    tag=permission_sync_tag,
    name=permission_sync_name,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/permission_syncs/',
        method=pages.FrontActionMethod.GET
    )
)

edit_page = pages.FormPage(
    name=_("编辑权限数据同步配置"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/permission_syncs/{id}/',
        method=pages.FrontActionMethod.GET
    )
)

edit_page.add_global_actions(
    [
        pages.ConfirmAction(path="/api/v1/tenant/{tenant_id}/permission_syncs/{id}/"),
        pages.CancelAction(),
        pages.ResetAction(),
    ]
)

create_page = pages.FormPage(
    name=_("创建一个新的权限数据同步配置"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/permission_syncs/',
        method=pages.FrontActionMethod.POST
    )
)

create_page.add_global_actions(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/permission_syncs/",
            action_type=pages.FrontActionType.DIRECT_ACTION,
            icon="icon-confirm"
        ),
        pages.CancelAction(),
        pages.ResetAction(),
    ]
)

page.add_local_action(
    [
        pages.FrontAction(
            name=_("同步"),
            method=pages.FrontActionMethod.GET,
            path="/api/v1/tenant/{tenant_id}/permission_syncs/{id}/sync/",
            action_type=pages.FrontActionType.DIRECT_ACTION
        ),
        pages.FrontAction(
            name=_("编辑"),
            page=edit_page,
            icon="icon-edit",
            action_type=pages.FrontActionType.OPEN_ACTION
        ),
        pages.FrontAction(
            name=_("删除"),
            method=pages.FrontActionMethod.DELETE,
            path="/api/v1/tenant/{tenant_id}/permission_syncs/{id}/",
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

page.add_global_actions(
    [
        pages.FrontAction(
            name="创建",
            page=create_page,
            icon="icon-create",
            action_type=pages.FrontActionType.OPEN_ACTION
        )
    ]
)


router = routers.FrontRouter(
    path=permission_sync_tag,
    name=permission_sync_name,
    page=page,
)

pages.register_front_pages(page)
pages.register_front_pages(create_page)
pages.register_front_pages(edit_page)