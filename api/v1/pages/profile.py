from openapi.utils import extend_schema_tags

tag = 'profile'
path = tag
name = '个人资料'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/user/info/',
            'method': 'get'
        }
    }
)