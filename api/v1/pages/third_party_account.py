from openapi.utils import extend_schema_tags

tag = 'third_party_account'
path = tag
name = '第三方账号绑定'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/user/bind_info/',
            'method': 'get'
        }
    }
)