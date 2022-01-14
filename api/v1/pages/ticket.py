from openapi.utils import extend_schema_tags

tag = 'ticket_manage'
path = 'ticket_manage'
name = '工单/待办管理'

ticket_manage_tag = 'ticket_manage'
ticket_manage_name = '工单/待办管理'

extend_schema_tags(
    ticket_manage_tag,
    ticket_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=ticket',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'ticket_manage.create',
                'description': '创建工单',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'ticket_manage.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=ticket',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

ticket_manage_create_tag = 'ticket_manage.create'
ticket_manage_create_name = '创建新工单'

extend_schema_tags(
    ticket_manage_create_tag,
    ticket_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

ticket_manage_update_tag = 'ticket_manage.update'
ticket_manage_update_name = '编辑工单'

extend_schema_tags(
    ticket_manage_update_tag,
    ticket_manage_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
