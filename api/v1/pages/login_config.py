from openapi.utils import extend_schema_tags

tag = 'lr_config'
path = tag
name = '登录注册配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/config/{subject}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'tag': 'lr_config_update'
            }
        }
    }
)

lr_config_update_tag = 'lr_config_update'
lr_config_update_name = '编辑登录注册配置信息'

extend_schema_tags(
    lr_config_update_tag,
    lr_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/config/{subject}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/config/{subject}/',
                'method': 'patch'
            }
        }
    }
)