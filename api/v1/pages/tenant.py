from openapi.utils import extend_schema_tags

tag = 'tenant'
path = tag
name = '租户管理'


from openapi.utils import extend_schema_tags

tag = 'tenant'
path = tag
name = '租户管理'


extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'tenant.create'
            }
        }
    }
)

tenant_create_tag = 'tenant.create'
tenant_create_name = '创建租户'

extend_schema_tags(
    tenant_create_tag,
    tenant_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/',
                'method': 'post'
            }
        }
    }
)