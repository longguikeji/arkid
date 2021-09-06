from openapi.utils import extend_schema_tags

tag = [ 'user_token_manage' ]
path = 'ulog'
name = '登录记录'

extend_schema_tags(
    tag,
    name
)

user_token_manage_tag = 'user_token_manage'
user_token_manage_name = 'Token管理'

extend_schema_tags(
    user_token_manage_tag,
    user_token_manage_name,
    {
        'type': 'form_page',
        'global': {
            'token': {
                'path': '/api/v1/user/token_expire/',
                'method': 'get',
                'description': '重置Token'
            }
        }
    }
)