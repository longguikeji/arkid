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
        'global': {
            'bind_agent': {
                'tag': 'bind_agent',
                'description': '绑定代理商',
            }
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

bind_agent_tag = 'bind_agent'
bind_agent_name = '绑定代理商'

extend_schema_tags(
    bind_agent_tag,
    bind_agent_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/arkstore/bind_agent/',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/arkstore/bind_agent/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)