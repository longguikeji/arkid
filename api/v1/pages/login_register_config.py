from openapi.utils import extend_schema_tags

tag = ['login_register_extension_config', 'tenant_register_privacy_notice', 'login_register_config']
path = 'settings'
name = '登录注册配置'

login_register_extension_config_tag = 'login_register_extension_config'
login_register_extension_config_name = '登录注册插件化配置'

extend_schema_tags(
    login_register_extension_config_tag,
    login_register_extension_config_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/login_register_config/?tenant={parent_lookup_tenant}',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'login_register_extension_config.create',
                'description': '添加租户登录注册插件'
            }
        },
        'local': {
            'update': {
                'tag': 'login_register_extension_config.update',
                'description': '编辑'
            },
            'delete': {
                'path': '/api/v1/login_register_config/{id}/?tenant={parent_lookup_tenant}',
                'method': 'delete',
                'description': '删除'
            }
        }
    }
)

login_register_extension_config_create_tag = 'login_register_extension_config.create'
login_register_extension_config_create_name = '添加租户登录注册插件'

extend_schema_tags(
    login_register_extension_config_create_tag,
    login_register_extension_config_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/login_register_config/?tenant={parent_lookup_tenant}',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/login_register_config/?tenant={parent_lookup_tenant}',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

login_register_extension_config_update_tag = 'login_register_extension_config.update'
login_register_extension_config_update_name = '编辑登录注册插件配置'

extend_schema_tags(
    login_register_extension_config_update_tag,
    login_register_extension_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/login_register_config/{id}/?tenant={parent_lookup_tenant}',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/login_register_config/{id}/?tenant={parent_lookup_tenant}',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

tenant_register_privacy_notice_tag = 'tenant_register_privacy_notice'
tenant_register_privacy_notice_name = '租户注册隐私声明'

extend_schema_tags(
    tenant_register_privacy_notice_tag,
    tenant_register_privacy_notice_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/config/privacy_notice/?tenant={tenant_uuid}',
            'method': 'get',
        },
        'global': {
            'update': {
                'tag': 'tenant_register_privacy_notice.update',
                'description': '编辑'
            }
        }
    }
)

tenant_register_privacy_notice_update_tag = 'tenant_register_privacy_notice.update'
tenant_register_privacy_notice_update_name = '编辑租户注册隐私声明'

extend_schema_tags(
    tenant_register_privacy_notice_update_tag,
    tenant_register_privacy_notice_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/config/privacy_notice/?tenant={tenant_uuid}',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/config/privacy_notice/?tenant={tenant_uuid}',
                'method': 'put',
                'description': '确定'
            }
        },
    },
)

login_register_config_tag = 'login_register_config'
login_register_config_name = '登录注册配置信息'

extend_schema_tags(
    login_register_config_tag,
    login_register_config_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/config/',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'login_register_config.update',
                'description': '编辑'
            }
        }
    }
)

login_register_config_update_tag = 'login_register_config.update'
login_register_config_update_name = '编辑登录注册配置信息'

extend_schema_tags(
    login_register_config_update_tag,
    login_register_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/config/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/config/',
                'method': 'patch',
                'description': '确定'
            }
        }
    }
)