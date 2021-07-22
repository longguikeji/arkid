from openapi.utils import extend_schema_tags

tag = 'tenant_config'
path = tag
name = '租户配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/tenant/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'tag': 'tenant_update'
            },
            'delete': {
                'path': '/api/v1/tenant/{id}/',
                'method': 'delete'
            } 
        }
    }
)

tenant_update_tag = 'tenant_update'
tenant_update_name = '编辑租户'

extend_schema_tags(
    tenant_update_tag,
    tenant_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{id}/',
                'method': 'put'
            }
        }
    }
)