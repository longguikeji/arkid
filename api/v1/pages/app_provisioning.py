from openapi.utils import extend_schema_tags

tag = 'app_provisioning'
path = tag
name = '应用管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/',
                'method': 'post'
            }
        },
        'item': {
            'mapping': 'app_provisioning_mapping',
            'profile': 'app_provisioning_profile',
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
                'method': 'delete'
            }
        },
    }
)
