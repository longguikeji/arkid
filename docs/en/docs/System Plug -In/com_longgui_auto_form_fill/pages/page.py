from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'auto_form_fill_account_manage'
name = '账密代填账户'

auto_form_fill_account_page = pages.TablePage(tag=tag, name=name)
auto_form_fill_account_edit_page = pages.FormPage(name=_("编辑账密代填账户"))

pages.register_front_pages(auto_form_fill_account_page)
pages.register_front_pages(auto_form_fill_account_edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=auto_form_fill_account_page,
    icon='list',
)

auto_form_fill_account_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_auto_form_fill/auto_form_fill/accounts/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/com_longgui_auto_form_fill/auto_form_fill/accounts/',
        ),
    },
    local_actions={
        "edit": actions.EditAction(
            page=auto_form_fill_account_edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/com_longgui_auto_form_fill/auto_form_fill/accounts/{id}/",
        )
    },
)

auto_form_fill_account_edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_auto_form_fill/auto_form_fill/accounts/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            method=actions.FrontActionMethod.PUT,
            path="/api/v1/tenant/{tenant_id}/com_longgui_auto_form_fill/auto_form_fill/accounts/{id}/"
        ),
    }
)