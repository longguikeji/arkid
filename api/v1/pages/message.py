from openapi.utils import extend_schema_tags

tag = ['message_manage']
path = 'message_manage'
name = '消息管理'

message_manage_tag = 'message_manage'
message_manage_name = '消息管理'

extend_schema_tags(
    message_manage_tag,
    message_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'message_manage.create',
                'description': '创建新消息',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'message_manage.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

message_manage_create_tag = 'message_manage.create'
message_manage_create_name = '创建新消息'

extend_schema_tags(
    message_manage_create_tag,
    message_manage_create_name,
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

message_manage_update_tag = 'message_manage.update'
message_manage_update_name = '编辑消息'

extend_schema_tags(
    message_manage_update_tag,
    message_manage_update_name,
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
