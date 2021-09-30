from openapi.utils import extend_schema_tags

tag = 'log_config'
path = tag
name = '日志设置'

extend_schema_tags(
    tag, name, {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/log_config/',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'log_config.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            }
        }
    })

log_config_update_tag = 'log_config.update'
log_config_update_name = '编辑日志配置'

extend_schema_tags(
    log_config_update_tag, log_config_update_name, {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/log_config/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/log_config/',
                'method': 'patch',
                'description': '确定'
            }
        }
    })