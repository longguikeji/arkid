from openapi.utils import extend_schema_tags

tag = 'backend_login'
path = tag
name = '后端认证'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'backend_login.create',
                'description': '添加后端认证',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'sort': {
                'up': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/move_up/',
                    'method': 'get'
                },
                'down': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/move_down/',
                    'method': 'get'
                },
                'top': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/move_top/',
                    'method': 'get'
                },
                'bottom': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/move_bottom/',
                    'method': 'get'
                },
                'batch': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/batch_update/',
                    'method': 'post'
                }
            },
            'update': {
                'tag': 'backend_login.update',
                'description': '编辑',
                'icon': 'el-icon-edit',
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)


backend_login_create_tag = 'backend_login.create'
backend_login_create_name = '创建后端认证'

extend_schema_tags(
    backend_login_create_tag,
    backend_login_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

backend_login_update_tag = 'backend_login.update'
backend_login_update_name = '编辑后端认证'

extend_schema_tags(
    backend_login_update_tag,
    backend_login_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/backend_login/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)