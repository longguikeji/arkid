from openapi.utils import extend_schema_tags

tag = 'permission_list'
path = tag
name = '权限列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'permission_list.create',
                'description': '添加权限',
                'icon': 'el-icon-plus',
            }
        },
        'local': {
            'update': {
                'tag': 'permission_list.update',
                'description': '编辑',
                'icon': 'el-icon-edit',
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/permission/{permission_uuid}/detail',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

permission_list_create_tag = 'permission_list.create'
permission_list_create_name = '添加权限'

extend_schema_tags(
    permission_list_create_tag,
    permission_list_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/permission/create',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/permission/create',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

permission_list_update_tag = 'permission_list.update'
permission_list_update_name = '编辑权限'

extend_schema_tags(
    permission_list_update_tag,
    permission_list_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/permission/{permission_uuid}/detail',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/permission/{permission_uuid}/detail',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

permission_only_list_tag = 'permission_only_list'
permission_only_list_name = '权限列表'

extend_schema_tags(
    permission_only_list_tag,
    permission_only_list_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/',
            'method': 'get'
        }
    }
)