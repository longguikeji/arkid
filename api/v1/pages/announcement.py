from openapi.utils import extend_schema_tags

tag = ['announcement_manage']
path = 'announcement_manage'
name = '公告管理'

announcement_manage_tag = 'announcement_manage'
announcement_manage_name = '桌面公告管理'

extend_schema_tags(
    announcement_manage_tag,
    announcement_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/message/?type=announcement',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'announcement_manage.create',
                'description': '创建新公告',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'announcement_manage.update',
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

announcement_manage_create_tag = 'announcement_manage.create'
announcement_manage_create_name = '创建新公告'

extend_schema_tags(
    announcement_manage_create_tag,
    announcement_manage_create_name,
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

announcement_manage_update_tag = 'announcement_manage.update'
announcement_manage_update_name = '编辑公告'

extend_schema_tags(
    announcement_manage_update_tag,
    announcement_manage_update_name,
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
