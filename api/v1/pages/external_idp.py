from openapi.utils import extend_schema_tags

tag = 'external_idp'
path = tag
name = '第三方登录'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'external_idp.create',
                'description': '添加第三方登录',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'sort': {
                'up': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_up/',
                    'method': 'get'
                },
                'down': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_down/',
                    'method': 'get'
                },
                'top': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_top/',
                    'method': 'get'
                },
                'bottom': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_bottom/',
                    'method': 'get'
                },
                'batch': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/batch_update/',
                    'method': 'post'
                }
            },
            'update': {
                'tag': 'external_idp.update',
                'description': '编辑',
                'icon': 'el-icon-edit',
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)


external_idp_create_tag = 'external_idp.create'
external_idp_create_name = '创建第三方登录'

extend_schema_tags(
    external_idp_create_tag,
    external_idp_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

external_idp_update_tag = 'external_idp.update'
external_idp_update_name = '编辑第三方登录'

extend_schema_tags(
    external_idp_update_tag,
    external_idp_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)