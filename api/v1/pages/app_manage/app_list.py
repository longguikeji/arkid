from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

app_list_tag = 'app_list'
app_list_name = '应用列表'


page = pages.TablePage(
    tag=app_list_tag,
    name=app_list_name,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=pages.FrontActionMethod.GET
    )
)

app_edit_page = pages.FormPage(
    name=_("编辑应用"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/',
        method=pages.FrontActionMethod.GET
    )
)

app_edit_page.add_global_actions(
    [
        pages.ConfirmAction(path="/api/v1/tenant/{tenant_id}/apps/{id}/"),
        pages.CancelAction(),
        pages.ResetAction(),
    ]
)

app_create_page = pages.FormPage(
    name=_("创建一个新的应用"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=pages.FrontActionMethod.POST
    )
)

app_create_page.add_global_actions(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/apps/",
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
            name=_("编辑"),
            page=app_edit_page,
            icon="icon-edit",
            action_type=pages.FrontActionType.OPEN_ACTION
        ),
        pages.FrontAction(
            name=_("删除"),
            method=pages.FrontActionMethod.DELETE,
            path="/api/v1/tenant/{tenant_id}/apps/{id}/",
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

page.add_global_actions(
    [
        pages.FrontAction(
            name="创建",
            page=app_create_page,
            icon="icon-create",
            action_type=pages.FrontActionType.OPEN_ACTION
        )
    ]
)


router = routers.FrontRouter(
    path=app_list_tag,
    name='应用管理',
    icon='app',
    page=page,
)

pages.register_front_pages(page)
pages.register_front_pages(app_create_page)
pages.register_front_pages(app_edit_page)