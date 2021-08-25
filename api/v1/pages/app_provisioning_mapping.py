from openapi.utils import extend_schema_tags

tag = 'app_provisioning_mapping'
path = tag
name = ''

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/',
                'method': 'post'
            }
        },
        'item': {
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
                'method': 'delete'
            }
        },
    }
)
