from openapi.utils import extend_schema_tags

tag = 'bind_saas'
path = tag
name = '绑定中心平台'

extend_schema_tags(
    tag, name, {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/bind_saas/',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'bind_saas.update',
                'description': '绑定',
                'icon': 'el-icon-edit'
            }
        }
    })

bind_saas_create_tag = 'bind_saas.update'
bind_saas_create_name = '绑定'

extend_schema_tags(
    bind_saas_create_tag, bind_saas_create_name, {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/bind_saas/',
            'method': 'post'
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