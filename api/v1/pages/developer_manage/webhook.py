# Webhook
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'webhook'
name = 'Webhook'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑Webhook"))
# create_page = pages.FormPage( name=_("创建一个新的Webhook") )
history_page = pages.TablePage(tag="webhook_history", name=_("webhook历史记录"))
# history_detail_page = pages.DescriptionPage(name=_("webhook历史记录详情"))

pages.register_front_pages(page)
pages.register_front_pages(history_page)

pages.register_front_pages(edit_page)
# pages.register_front_pages(history_detail_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='webhook',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "create": actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/webhooks/',
        )
    },
    local_actions={
        "open": actions.OpenAction(
            name=_("历史记录"),
            page=history_page,
            icon="icon-edit",
        ),
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/webhooks/{id}/"
        ),
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/{id}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        "confirm": actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/webhooks/{id}/",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)

# create_page.create_actions(
#     # name=_("创建一个新的Webhook"),
#     init_action=actions.DirectAction(
#         path='/api/v1/tenant/{tenant_id}/webhooks/',
#         method=actions.FrontActionMethod.POST
#     ),
#     global_actions = {
#         "confirm": actions.ConfirmAction(
#             path="/api/v1/tenant/{tenant_id}/webhooks/"
#         ),
#     }
# )

history_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        # "open": actions.OpenAction(name=_("查阅"), page=history_detail_page),
        "direct": actions.DirectAction(
            name=_("重试"),
            path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/retry/',
            method=actions.FrontActionMethod.GET,
        ),
        "delete": actions.DeleteAction(
            path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/',
        ),
    },
)

# history_detail_page.create_actions(
#     init_action=actions.DirectAction(
#         path='/api/v1/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/',
#         method=actions.FrontActionMethod.GET,
#     )
# )
