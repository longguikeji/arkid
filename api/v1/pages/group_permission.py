from openapi.utils import extend_schema_tags

tag = [ 'group_list' ,'group_list.permission' ]
path = 'gpermission'
name = '组权限'

group_list_tag = 'group_list'
group_list_name = '所有分组'

extend_schema_tags(
    group_list_tag,
    group_list_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get',
            'next': 'group_list.permission'
        },
        'local': {
            'node': {
                'next': 'group_list.permission'
            }
        }
    }
)

group_permission_tag = 'group_list.permission'
group_permission_name = '组权限'

extend_schema_tags(
    group_permission_tag,
    group_permission_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/group_permission/{group_uuid}/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'group_list.permission.create',
                'description': '添加组权限',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/group_permission/{group_uuid}/delete/',
                'method': 'get',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

group_permission_create_tag = 'group_list.permission.create'
group_permission_create_name = '添加组权限'

extend_schema_tags(
    group_permission_create_tag,
    group_permission_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/group_permission/{group_uuid}/create',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/group_permission/{group_uuid}/create',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)