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
        'global': {
            'update': {
                'tag': 'tenant_config.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{id}/',
                'method': 'delete',
                'description': '注销租户',
                'icon': 'el-icon-circle-close'
            } 
        }
    }
)

tenant_update_tag = 'tenant_config.update'
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
        'global': {
            'update': {
                'path': '/api/v1/tenant/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)