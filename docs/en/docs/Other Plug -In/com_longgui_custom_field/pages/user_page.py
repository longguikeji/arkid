from arkid.core import pages, actions
from arkid.core.translation import gettext_default as _
from api.v1.pages.user_manage.user_list import page as user_list_page

custom_field_page = pages.TablePage(name=_("自定义字段"))
custom_field_edit_page = pages.FormPage(name=_("编辑自定义字段"))

pages.register_front_pages(custom_field_page)
pages.register_front_pages(custom_field_edit_page)

# 单独的页面配置
user_list_page.global_action['custom_field'] = actions.OpenAction(
    name=("自定义字段"),
    page=custom_field_page
)

custom_field_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_custom_field/custom_fields/?subject=user',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/com_longgui_custom_field/custom_fields/?subject=user',
        ),
    },
    local_actions={
        "edit": actions.EditAction(
            page=custom_field_edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/com_longgui_custom_field/custom_fields/{id}/",
        )
    },
)

custom_field_edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_custom_field/custom_fields/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            method=actions.FrontActionMethod.PUT,
            path="/api/v1/tenant/{tenant_id}/com_longgui_custom_field/custom_fields/{id}/"
        ),
    }
)