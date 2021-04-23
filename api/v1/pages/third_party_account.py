from openapi.utils import extend_schema_tags

tag = 'third_party_account'
path = tag
name = '第三方账号绑定'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/user/info/',
            'method': 'get'
        },
        'page': {
            'update': {
                'read': {
                    'path': '/api/v1/user/info/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/user/info/',
                    'method': 'post'
                }
            }
        }
    }
)