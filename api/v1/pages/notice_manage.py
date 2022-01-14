from openapi.utils import extend_schema_tags

tag = 'notice_manage'
path = 'notice_manage'
name = '通知管理'

notice_manage_tag = 'notice_manage'
notice_manage_name = '桌面通知管理'

extend_schema_tags(
    notice_manage_tag,
    notice_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=notice',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'notice_manage.create',
                'description': '创建新通知',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'notice_manage.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

notice_manage_create_tag = 'notice_manage.create'
notice_manage_create_name = '创建新通知'

extend_schema_tags(
    notice_manage_create_tag,
    notice_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

notice_manage_update_tag = 'notice_manage.update'
notice_manage_update_name = '编辑通知'

extend_schema_tags(
    notice_manage_update_tag,
    notice_manage_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/message/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
