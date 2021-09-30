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
        'global': {
            'update': {
                'tag': 'profile.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'password': {
                'path': '/api/v1/user/update_password/',
                'method': 'post',
                'description': '重置密码',
                'icon': 'el-icon-lock'
            },
            'logoff': {
                'path': '/api/v1/user/logoff/',
                'method': 'get',
                'description': '注销',
                'icon': 'el-icon-remove-outline'
            }
        }
    }
)

profile_update_tag = 'profile.update'
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
        'global': {
            'update': {
                'path': '/api/v1/user/info/',
                'method': 'patch',
                'description': '确定'
            }
        }
    }
)