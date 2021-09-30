from openapi.utils import extend_schema_tags

tag = 'tenant_switch'
path = tag
name = '平台配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/tenant_switch/',
            'method': 'get'
        },
        'local': {
            'item': {
                'path': '/api/v1/tenant_switch/',
                'method': 'put'
            }
        }
    }
)