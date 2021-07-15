from openapi.utils import extend_schema_tags

tag = 'app_list'
path = tag
name = '应用管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
                'method': 'post'
            }
        },
        'item': {
            'provisioning': 'app_provisioning',
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
                'method': 'delete'
            }
        },
    }
)
