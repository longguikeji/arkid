from openapi.utils import extend_schema_tags

tag = [ 'user_list', 'user_list.permission' ]
path = 'upermission'
name = '用户权限'

user_list_tag = 'user_list'
user_list_name = '用户列表'

extend_schema_tags(
    user_list_tag,
    user_list_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/user_list/',
            'method': 'get',
            'next': 'user_list.permission'
        },
        'local': {
            'node': {
                'next': 'user_list.permission'
            }
        }
    }
)

upermission_tag = 'user_list.permission'
upermission_name = '用户权限'

extend_schema_tags(
    upermission_tag,
    upermission_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/user_permission/{user_uuid}/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'user_list.permission.create',
                'description': '添加用户权限',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/user_permission/{user_uuid}/delete/',
                'method': 'get',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

upermission_create_tag = 'user_list.permission.create'
upermission_create_name = '添加用户权限'

extend_schema_tags(
    upermission_create_tag,
    upermission_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/user_permission/{user_uuid}/create',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/user_permission/{user_uuid}/create',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)