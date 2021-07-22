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
        },
        'page': {
            'update': {
                'tag': 'profile_update'
            },
            'password': {
                'path': '/api/v1/user/update_password/',
                'method': 'post'
            }
        }
    }
)

profile_update_tag = 'profile_update'
profile_update_name = '编辑个人资料'

extend_schema_tags(
    profile_update_tag,
    profile_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/user/info/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/user/info/',
                'method': 'patch'
            }
        }
    }
)