from openapi.utils import extend_schema_tags

tag = 'permission_group'
path = tag
name = '权限分组'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/permission_group/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'permission_group.create',
                'description': '创建',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'permission_group.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/permission_group/{permission_group_uuid}/detail',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

permission_group_create_tag = 'permission_group.create'
permission_group_create_name = '添加新的权限分组'

extend_schema_tags(
    permission_group_create_tag,
    permission_group_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/permission_group/create',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/permission_group/create',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

permission_group_update_tag = 'permission_group.update'
permission_group_update_name = '编辑权限分组'

extend_schema_tags(
    permission_group_update_tag,
    permission_group_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/permission_group/{permission_group_uuid}/detail',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/permission_group/{permission_group_uuid}/detail',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

permission_group_only_list_tag = 'permission_group_only_list'
permission_group_only_list_name = '权限分组列表'

extend_schema_tags(
    permission_group_only_list_tag,
    permission_group_only_list_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/permission_group/',
            'method': 'get'
        }
    }
)