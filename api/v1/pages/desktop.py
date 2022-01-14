from openapi.utils import extend_schema_tags
from django.conf import settings
from extension.models import Extension
from django.utils.translation import ugettext_lazy as _

tag = ['desktop', 'article']
path = 'desktop'
name = '桌面'

app_tag = 'desktop'
app_name = '应用市集'

extend_schema_tags(
        app_tag,
        app_name,
        {
            'type': 'list_page',
            'init': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{parent_lookup_user}/app/',
                'method': 'get'
            },
            # 取消多账号开关  官春元   2022-01-04
            # 'local': {
            #     'tag': 'multiple_account_edit',
            #     'description': '多账号开关'
            # },
            'global': {
                'manage':{
                    'tag': 'app_manage',
                    'description': '管理应用'      
                }
            }
        }
    )

app_manage_tag = 'app_manage'
app_manage_name = '管理应用'

extend_schema_tags(
    app_manage_tag,
    app_manage_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{parent_lookup_user}/app_subscribe_list/',
            'method': 'get'
        },
        'local': {
            'item': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/user/{parent_lookup_user}/subscribe/',
                'method': 'post'
            }
        }
    }
)
# 取消多账号开关  官春元   2022-01-04
# desktop_app_edit_tag = 'multiple_account_edit'
# desktop_app_edit_name = '多账号开关'

# extend_schema_tags(
#     desktop_app_edit_tag,
#     desktop_app_edit_name,
#     {
#         'type': 'form_page',
#         'init': {
#             'path': '/api/v1/tenant/{tenant_uuid}/app/{app_id}/user_application_multiple_account_switch/',
#             'method': 'get'
#         },
#         'local': {
#             'item': {
#                 'path': '/api/v1/tenant/{tenant_uuid}/app/{app_id}/user_application_multiple_account_switch/',
#                 'method': 'put'
#             }
#         }
#     }
# )

# notice_tag = 'notice'
# notice_name = '通知列表'

# extend_schema_tags(
#     notice_tag,
#     notice_name,
#     {
#         'init': {
#             'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=notice',
#             'method': 'get'
#         }
#     }
# )

# ticket_tag = 'ticket'
# ticket_name = '待办提醒'

# extend_schema_tags(
#     ticket_tag,
#     ticket_name,
#     {
#         'init': {
#             'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=ticket',
#             'method': 'get'
#         }
#     }
# )

article_tag = 'article'
article_name = '知识驿站'

extend_schema_tags(
    article_tag,
    article_name,
    {
        'type': 'list_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/',
            'method': 'get'
        }
    }
)

# announcement_tag = 'announcement'
# announcement_name = '公告列表'

# extend_schema_tags(
#     announcement_tag,
#     announcement_name,
#     {
#         'init': {
#             'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=announcement',
#             'method': 'get'
#         }
#     }
# )
