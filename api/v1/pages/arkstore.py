from openapi.utils import extend_schema_tags

tag = 'arkstore'
path = tag
name = '插件商店'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'dashboard_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/arkstore/',
            'method': 'get'
        },
        'local': {
            'purchase': {
                'path': '/api/v1/tenant/{tenant_uuid}/arkstore/order/',
                'method': 'post',
                'description': '购买'
            },
            'install': {
                'path': '/api/v1/tenant/{tenant_uuid}/arkstore/install/{id}/',
                'method': 'get',
                'description': '安装'
            },
            'upgrade': {
                'path': '/api/v1/tenant/{tenant_uuid}/arkstore/install/{id}/',
                'method': 'get',
                'description': '升级'
            }
        }
    }
)