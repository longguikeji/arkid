from openapi.utils import extend_schema_tags

tag = 'desktop_config'
path = tag
name = '桌面设置'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/desktopconfig/',
            'method': 'get'
        },
        'local': {
            'item': {
                'path': '/api/v1/tenant/{tenant_uuid}/desktopconfig/',
                'method': 'put'
            }
        }
    }
)