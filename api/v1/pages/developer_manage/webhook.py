# Webhook
from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

webhook_tag = 'webhook'
webhook_name = 'Webhook'


page = pages.TablePage(
    tag=webhook_tag,
    name=webhook_name,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/',
        method=pages.FrontActionMethod.GET,
        action_type=pages.FrontActionType.DIRECT_ACTION
    )
)

edit_page = pages.FormPage(
    name=_("编辑Webhook"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/{id}/',
        method=pages.FrontActionMethod.GET,
        action_type=pages.FrontActionType.DIRECT_ACTION
    )
)

edit_page.add_global_actions(
    [
        pages.ConfirmAction(path="/api/v1/tenant/{tenant_id}/webhooks/{id}/"),
        pages.CancelAction(),
        pages.ResetAction(),
    ]
)

create_page = pages.FormPage(
    name=_("创建一个新的Webhook"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/',
        method=pages.FrontActionMethod.POST,
        action_type=pages.FrontActionType.DIRECT_ACTION
    )
)

create_page.add_global_actions(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/webhooks/",
            action_type=pages.FrontActionType.DIRECT_ACTION,
            icon="icon-confirm"
        ),
        pages.CancelAction(),
        pages.ResetAction(),
    ]
)

history_page = pages.TablePage(
    name=_("webhook历史记录"),
    tag="webhook_history",
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/',
        method=pages.FrontActionMethod.GET,
        action_type=pages.FrontActionType.DIRECT_ACTION
    )
)

history_page.add_local_action(
    [
        pages.FrontAction(
            name=_("查阅"),
            path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/',
            method=pages.FrontActionMethod.GET,
            action_type=pages.FrontActionType.DIRECT_ACTION
        ),
        pages.FrontAction(
            name=_("重试"),
            path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/retry/',
            method=pages.FrontActionMethod.GET,
            action_type=pages.FrontActionType.DIRECT_ACTION
        ),
        pages.FrontAction(
            name=_("删除"),
            method=pages.FrontActionMethod.DELETE,
            path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/',
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

page.add_local_action(
    [
        pages.FrontAction(
            name=_("历史记录"),
            page=history_page,
            icon="icon-edit",
            action_type=pages.FrontActionType.OPEN_ACTION
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
            path="/api/v1/tenant/{tenant_id}/webhooks/{id}/",
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
    path=webhook_tag,
    name=webhook_name,
    page=page,
)

pages.register_front_pages(history_page)
pages.register_front_pages(page)
pages.register_front_pages(create_page)
pages.register_front_pages(edit_page)