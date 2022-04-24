from arkid.core import routers, pages
from arkid.core.translation import gettext_default as _

app_list_tag = 'app_list'
app_list_name = '应用列表'


page = pages.FrontPage(
    tag=app_list_tag,
    name=app_list_name,
    page_type=pages.FrontPageType.TABLE_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=pages.FrontActionMethod.GET
    )
)

app_edit_page = pages.FrontPage(
    name=_("编辑应用"),
    page_type=pages.FrontPageType.FORM_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/',
        method=pages.FrontActionMethod.GET
    )
)

app_edit_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/apps/{id}/",
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

app_create_page = pages.FrontPage(
    name=_("创建一个新的应用"),
    page_type=pages.FrontPageType.FORM_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=pages.FrontActionMethod.POST
    )
)

app_create_page.add_global_action(
    [
        pages.FrontAction(
            method=pages.FrontActionMethod.POST,
            name=_("确认"),
            path="/api/v1/tenant/{tenant_id}/apps/",
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
            path="/api/v1/tenant/{tenant_id}/apps/{id}/",
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
    path=app_list_tag,
    name='应用管理',
    icon='app',
    page=page,
)

pages.register_front_pages(page)
pages.register_front_pages(app_create_page)
pages.register_front_pages(app_edit_page)