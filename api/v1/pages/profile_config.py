from openapi.utils import extend_schema_tags

tag = 'profile_config'
path = tag
name = '个人资料设置'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'profile_config.update'
            }
        }
    }
)

profile_config_update_tag = 'profile_config.update'
profile_config_update_name = '编辑个人资料设置'

extend_schema_tags(
    profile_config_update_tag,
    profile_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/userconfig',
                'method': 'put'
            }
        }
    }
)