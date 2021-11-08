from openapi.utils import extend_schema_tags

tag = 'multiple_ips'
path = 'multiple_ips'
name = '多网段应用管理'


extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/multiple_ips/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'multiple_ips.create',
                'description': '创建新通知',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'multiple_ips.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/multiple_ips/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

multiple_ips_create_tag = 'multiple_ips.create'
multiple_ips_create_name = '创建新通知'

extend_schema_tags(
    multiple_ips_create_tag,
    multiple_ips_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/multiple_ips/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/multiple_ips/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

multiple_ips_update_tag = 'multiple_ips.update'
multiple_ips_update_name = '编辑通知'

extend_schema_tags(
    multiple_ips_update_tag,
    multiple_ips_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/multiple_ips/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/multiple_ips/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
