from openapi.utils import extend_schema_tags

tag = 'data_sync'
path = tag
name = '数据同步'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'data_sync.create',
                'description': '添加数据同步配置',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'data_sync.update',
                'description': '编辑',
                'icon': 'el-icon-edit',
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)


data_sync_create_tag = 'data_sync.create'
data_sync_create_name = '创建数据同步配置'

extend_schema_tags(
    data_sync_create_tag,
    data_sync_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

data_sync_update_tag = 'data_sync.update'
data_sync_update_name = '编辑数据同步配置'

extend_schema_tags(
    data_sync_update_tag,
    data_sync_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)


data_sync_table_tag = 'data_sync_table'
data_sync_table_name = '同步服务端列表'

extend_schema_tags(
    data_sync_table_tag,
    data_sync_table_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/data_sync/',
            'method': 'get'
        }
    }
)
