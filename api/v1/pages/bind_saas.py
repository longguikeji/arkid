from openapi.utils import extend_schema_tags

tag = 'bind_saas'
path = tag
name = '绑定中心平台'

extend_schema_tags(
    tag, name, {
        'type': 'description_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/bind_saas/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'bind_saas.create',
                'description': '绑定',
                'icon': 'el-icon-edit'
            }
        }
    })

bind_saas_create_tag = 'bind_saas.create'
bind_saas_create_name = '绑定'

extend_schema_tags(
    bind_saas_create_tag, bind_saas_create_name, {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/bind_saas/',
            'method': 'get'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/bind_saas/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)