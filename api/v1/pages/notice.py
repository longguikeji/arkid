from openapi.utils import extend_schema_tags

tag = [ 'notice', 'ticket', 'announcement' ]
path = 'notice'
name = '分组管理'

notice_tag = 'notice'
notice_name = '通知列表'

extend_schema_tags(
    notice_tag,
    notice_name,
    {
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=notice',
            'method': 'get'
        },
#         'global': {
#             'create': {
#                 'tag': 'notice_manage.create',
#                 'description': '创建新通知',
#                 'icon': 'el-icon-plus'
#             }
#         },
#         'local': {
#             'update': {
#                 'tag': 'notice_manage.update',
#                 'description': '编辑',
#                 'icon': 'el-icon-edit'
#             },
#             'delete': {
#                 'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
#                 'method': 'delete',
#                 'description': '删除',
#                 'icon': 'el-icon-delete'
#             }
#         }
    }
)

ticket_tag = 'ticket'
ticket_name = '待办提醒'

extend_schema_tags(
    ticket_tag,
    ticket_name,
    {
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=ticket',
            'method': 'get'
        }
    }
)

announcement_tag = 'announcement'
announcement_name = '公告列表'

extend_schema_tags(
    announcement_tag,
    announcement_name,
    {
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=ticket',
            'method': 'get'
        }
    }
)
