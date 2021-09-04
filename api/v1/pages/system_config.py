from openapi.utils import extend_schema_tags

tag = [ 'system_login_register_extension', 'system_config', 'system_register_privacy_notice' ]
path = 'system_lrconfig'
name = '系统配置'

system_login_register_extension_tag = 'system_login_register_extension'
system_login_register_extension_name = '系统平台登录注册插件化配置'

extend_schema_tags(
    system_login_register_extension_tag,
    system_login_register_extension_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/login_register_config/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'system_login_register_extension.create'
            }
        },
        'local': {
            'update': {
                'tag': 'system_login_register_extension.update'
            },
            'delete': {
                'path': '/api/v1/login_register_config/{id}/',
                'method': 'delete'
            }
        }
    }
)

system_login_register_extension_create_tag = 'system_login_register_extension.create'
system_login_register_extension_create_name = '创建系统平台登录注册插件'

extend_schema_tags(
    system_login_register_extension_create_tag,
    system_login_register_extension_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/login_register_config/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/login_register_config/',
                'method': 'post'
            }
        }
    }
)

system_login_register_extension_update_tag = 'system_login_register_extension.update'
system_login_register_extension_update_name = '编辑系统平台登录注册插件'

extend_schema_tags(
    system_login_register_extension_update_tag,
    system_login_register_extension_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/login_register_config/{id}/',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/login_register_config/{id}/',
                'method': 'put'
            }
        }
    }
)

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
            'path': '/api/v1/config/privacy_notice/',
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
            'path': '/api/v1/config/privacy_notice/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/config/privacy_notice/',
                'method': 'put'
            }
        }
    }
)