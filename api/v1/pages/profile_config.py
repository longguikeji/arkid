from openapi.utils import extend_schema_tags

tag = [ 'profile_config_editfields', 'profile_config_logout', 'profile_config_logging', 'profile_config_token' ]
path = 'pconfig'
name = '个人资料设置'

profile_config_editfields_tag = 'profile_config_editfields'
profile_config_editfields_name = '个人资料之可编辑字段列表'

extend_schema_tags(
    profile_config_editfields_tag,
    profile_config_editfields_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/editfields',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'profile_config_editfields.update',
                'description': '设置可编辑字段'
            }
        }
    }
)

profile_config_editfields_update_tag = 'profile_config_editfields.update'
profile_config_editfields_update_name = '添加或删除可编辑字段'

extend_schema_tags(
    profile_config_editfields_update_tag,
    profile_config_editfields_update_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/editfield',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/userconfig/editfield',
                'method': 'put',
                'description': '确定编辑'
            }
        }
    }
)


profile_config_logout_tag = 'profile_config_logout'
profile_config_logout_name = '个人资料之注销配置'

extend_schema_tags(
    profile_config_logout_tag,
    profile_config_logout_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/logout',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'profile_config_logout.update',
                'description': '编辑'
            }
        }
    }
)

profile_config_logout_update_tag = 'profile_config_logout.update'
profile_config_logout_update_name = '编辑个人资料之注销配置'

extend_schema_tags(
    profile_config_logout_update_tag,
    profile_config_logout_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/logout',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/userconfig/logout',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

profile_config_logging_tag = 'profile_config_logging'
profile_config_logging_name = '个人资料之设备记录配置'

extend_schema_tags(
    profile_config_logging_tag,
    profile_config_logging_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/logging',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'profile_config_logging.update',
                'description': '编辑'
            }
        }
    }
)

profile_config_logging_update_tag = 'profile_config_logging.update'
profile_config_logging_update_name = '编辑个人资料之设备记录配置'

extend_schema_tags(
    profile_config_logging_update_tag,
    profile_config_logging_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/logging',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/userconfig/logging',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

profile_config_token_tag = 'profile_config_token'
profile_config_token_name = '个人资料之Token配置'

extend_schema_tags(
    profile_config_token_tag,
    profile_config_token_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/token',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'profile_config_token.update',
                'description': '编辑'
            }
        }
    }
)

profile_config_token_update_tag = 'profile_config_token.update'
profile_config_token_update_name = '编辑个人资料之Token配置'

extend_schema_tags(
    profile_config_token_update_tag,
    profile_config_token_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/userconfig/token',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/userconfig/token',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)