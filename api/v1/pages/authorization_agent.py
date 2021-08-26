from openapi.utils import extend_schema_tags

tag = 'authorization_agent'
path = tag
name = '身份源代理'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'authorization_agent.create'
            }
        },
        'local': {
            'sort': {
                'up': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/move_up/',
                    'method': 'get'
                },
                'down': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/move_down/',
                    'method': 'get'
                },
                'top': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/move_top/',
                    'method': 'get'
                },
                'bottom': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/move_bottom/',
                    'method': 'get'
                },
                'batch': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/batch_update/',
                    'method': 'post'
                }
            },
            'update': {
                'tag': 'authorization_agent.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/',
                'method': 'delete'
            }
        }
    }
)


authorization_agent_create_tag = 'authorization_agent.create'
authorization_agent_create_name = '创建身份源代理'

extend_schema_tags(
    authorization_agent_create_tag,
    authorization_agent_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/',
                'method': 'post'
            }
        }
    }
)

authorization_agent_update_tag = 'authorization_agent.update'
authorization_agent_update_name = '编辑身份源代理'

extend_schema_tags(
    authorization_agent_update_tag,
    authorization_agent_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_agent/{id}/',
                'method': 'put'
            }
        }
    }
)