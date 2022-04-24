from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

app_group_tag = 'app_group'
app_group_name = '应用分组'


page = pages.TablePage(
    tag=app_group_tag,
    name=app_group_name,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/',
        method=pages.FrontActionMethod.GET
    )
)

app_edit_page = pages.FormPage(
    name=_("编辑应用分组"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/{id}/',
        method=pages.FrontActionMethod.GET
    )
)

app_edit_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/app_groups/{id}/",
            icon="icon-confirm"
        ),
        pages.FrontAction(
            name=_("取消"),
            action_type=pages.FrontActionType.CANCEL_ACTION,
            icon="icon-cancel"
        ),
        pages.FrontAction(
            name=_("重置"),
            action_type=pages.FrontActionType.RESET_ACTION,
            icon="icon-reset"
        ),
    ]
)

app_create_page = pages.FormPage(
    name=_("创建一个新的应用分组"),
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/',
        method=pages.FrontActionMethod.POST
    )
)

app_create_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/app_groups/",
            action_type=pages.FrontActionType.DIRECT_ACTION,
            icon="icon-confirm"
        ),
        pages.FrontAction(
            name=_("取消"),
            action_type=pages.FrontActionType.CANCEL_ACTION,
            icon="icon-cancel"
        ),
        pages.FrontAction(
            name=_("重置"),
            action_type=pages.FrontActionType.RESET_ACTION,
            icon="icon-reset"
        ),
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
            path="/api/v1/tenant/{tenant_id}/app_groups/{id}/",
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

page.add_global_action(
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
    path=app_group_tag,
    name='应用分组',
    page=page,
)

pages.register_front_pages(page)
pages.register_front_pages(app_create_page)
pages.register_front_pages(app_edit_page)