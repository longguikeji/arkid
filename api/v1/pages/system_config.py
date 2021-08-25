from openapi.utils import extend_schema_tags

tag = [ 'system_config', 'system_register_privacy_notice' ]
path = 'system_config'
name = '系统配置'

system_config_tag = 'system_config'
system_config_name = '系统配置'

extend_schema_tags(
    system_config_tag,
    system_config_name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/system/config',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'system_config.update'
            }
        }
    }
)

system_config_update_tag = 'system_config.update'
system_config_update_name = '编辑系统配置信息'

extend_schema_tags(
    system_config_update_tag,
    system_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/system/config',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/system/config',
                'method': 'put'
            }
        }
    }
)

system_register_privacy_notice_tag = 'system_register_privacy_notice'
system_register_privacy_notice_name = '系统注册隐私声明'

extend_schema_tags(
    system_register_privacy_notice_tag,
    system_register_privacy_notice_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/system/config/privacy_notice/',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'system_register_privacy_notice.update'
            }
        }
    }
)

system_register_privacy_notice_update_tag = 'system_register_privacy_notice.update'
system_register_privacy_notice_update_name = '编辑系统注册隐私声明'

extend_schema_tags(
    system_register_privacy_notice_update_tag,
    system_register_privacy_notice_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/system/config/privacy_notice/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/system/config/privacy_notice/',
                'method': 'put'
            }
        }
    }
)