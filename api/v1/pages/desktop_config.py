from openapi.utils import extend_schema_tags

tag = 'desktop_config'
path = tag
name = '桌面设置'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/desktopconfig/',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'desktop_config.update',
                'description': '编辑'
            }
        }
    }
)

desktop_config_update_tag = 'desktop_config.update'
desktop_config_update_name = '编辑桌面应用列表配置'

extend_schema_tags(
    desktop_config_update_tag,
    desktop_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/desktopconfig/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/desktopconfig/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
