from openapi.utils import extend_schema_tags

tag = [ 'group', 'group_user' ]
path = 'gmanage'
name = '分组管理'

group_tree_tag = 'group_tree'
group_tree_name = '选择分组'

extend_schema_tags(
    group_tree_tag,
    group_tree_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'local': {
            'children': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={id}',
                'method': 'get'
            }
        }
    }
)

group_tag = 'group'
group_name = '分组'

extend_schema_tags(
    group_tag,
    group_name,
    {
        'type':'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'group.create'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/group_import/',
                'method': 'post'
            },
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/group_export/',
                'method': 'get'
            }
        },
        'local': {
            'update': {
                'tag': 'group.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                'method': 'delete'
            },
            'children': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={id}',
                'method': 'get'
            }
        }
    }
)

group_create_tag = 'group.create'
group_create_name = '创建组'

extend_schema_tags(
    group_create_tag,
    group_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
                'method': 'post'
            }
        }
    }
)

group_update_tag = 'group.update'
group_update_name = '编辑组'

extend_schema_tags(
    group_update_tag,
    group_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                'method': 'put'
            }
        }
    }
)

group_user_tag = 'group_user'
group_user_name = '组用户'

extend_schema_tags(
    group_user_tag,
    group_user_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'get'
        },
        'global': {
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                'method': 'get'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                'method': 'post'
            }
        }
    }
)

group_tree_tag = 'group_tree'
group_tree_name = '分组'

extend_schema_tags(
    group_tree_tag,
    group_tree_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        }
    }
)