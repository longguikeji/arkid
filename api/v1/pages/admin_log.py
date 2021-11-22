from openapi.utils import extend_schema_tags

tag = 'admin_log'
path = tag
name = '管理员行为日志'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/admin_log/',
            'method': 'get'
        },
        'local': {
            'detail': {
                'tag': 'admin_log.detail',
                'icon': 'el-icon-reading',
                'description': '查看详情'
            }
        }
    }
)

admin_log_detail_tag = 'admin_log.detail'
admin_log_detail_name = '用户行为日志详情'

extend_schema_tags(
    admin_log_detail_tag,
    admin_log_detail_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/admin_log/{id}/',
            'method': 'get'
        }
    }
)