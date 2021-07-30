from openapi.utils import extend_schema_tags

tag = 'user'
path = tag
name = '用户列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'user.create'
            },
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                'method': 'get'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                'method': 'post'
            }
        },
        'item': {
            'password': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/user/reset_password/',
                    'method': 'post'
                }
            },
            'update': {
                'tag': 'user.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                'method': 'delete'
            }
        }
    }
)

user_create_tag = 'user.create'
user_create_name = '创建用户'

extend_schema_tags(
    user_create_tag,
    user_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
                'method': 'post'
            }
        }
    }
)

user_update_tag = 'user.update'
user_update_name = '编辑用户'

extend_schema_tags(
    user_update_tag,
    user_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                'method': 'put'
            }
        }
    }
)