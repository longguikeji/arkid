from openapi.utils import extend_schema_tags

tag = 'tenant'
path = tag
name = '租户管理（新建租户获得管理员角色）'

extend_schema_tags(
    tag,
    name,
    {
        'type':'dashboard_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'tenant.create',
                'description': '新建租户',
                'icon': 'el-icon-plus'
            }
        }
    }
)

tenant_create_tag = 'tenant.create'
tenant_create_name = '新建租户'

extend_schema_tags(
    tenant_create_tag,
    tenant_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)