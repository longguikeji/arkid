from openapi.utils import extend_schema_tags

tag = 'user_log'
path = tag
name = '用户行为日志'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user_log/',
            'method': 'get'
        },
        'local': {
            'detail': {
                'tag': 'user_log.detail',
                'icon': 'el-icon-reading',
                'description': '查看详情'
            }
        }
    }
)

user_log_detail_tag = 'user_log.detail'
user_log_detail_name = '用户行为日志详情'

extend_schema_tags(
    user_log_detail_tag,
    user_log_detail_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/log/{id}/',
            'method': 'get'
        }
    }
)