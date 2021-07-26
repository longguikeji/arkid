from openapi.utils import extend_schema_tags

tag = 'gmanager'
path = tag
name = '分组管理'

extend_schema_tags(
    tag,
    name,
    [ 'group', 'group_user' ]
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
        'page': {
            'create': {
                'tag': 'group_create'
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
        'item': {
            'update': {
                'tag': 'group_update'
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

group_create_tag = 'group_create'
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
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
                'method': 'post'
            }
        }
    }
)

group_update_tag = 'group_update'
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
        'page': {
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
        'page': {
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
