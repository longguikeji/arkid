from openapi.utils import extend_schema_tags

tag = 'user'
path = tag
name = '用户列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'user.create',
                'description': '添加用户'
            },
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                'method': 'get',
                'description': '全部导出'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                'method': 'post',
                'description': '导入'
            },
            'custom': {
                'tag': 'user.custom_fields',
                'description': '自定义字段'
            }
        },
        'local': {
            'password': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                    'method': 'get',
                    'description': '设置密码'
                },
                'write': {
                    'path': '/api/v1/user/reset_password/',
                    'method': 'post',
                    'description': '设置密码'
                }
            },
            'update': {
                'tag': 'user.update',
                'description': '编辑'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                'method': 'delete',
                'description': '删除'
            }
        }
    }
)

user_create_tag = 'user.create'
user_create_name = '创建用户'

extend_schema_tags(
    user_create_tag,
    user_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

user_update_tag = 'user.update'
user_update_name = '编辑用户'

extend_schema_tags(
    user_update_tag,
    user_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

user_custom_fields_tag = 'user.custom_fields'
user_custom_fields_name = '添加用户自定义字段'

extend_schema_tags(
    user_custom_fields_tag,
    user_custom_fields_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/?subject=user',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'user.custom_fields.create',
                'description': '添加自定义字段'
            }
        },
        'local': {
            'update': {
                'tag': 'user.custom_fields.update',
                'description': '编辑'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/{id}/?subject=user',
                'method': 'delete',
                'description': '删除'
            }
        }
    }
)

user_custom_fields_create_tag = 'user.custom_fields.create'
user_custom_fields_create_name = '添加用户的自定义字段'

extend_schema_tags(
    user_custom_fields_create_tag,
    user_custom_fields_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/?subject=user',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

user_custom_fields_update_tag = 'user.custom_fields.update'
user_custom_fields_update_name = '编辑用户的自定义字段'

extend_schema_tags(
    user_custom_fields_update_tag,
    user_custom_fields_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/{id}/?subject=user',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/{id}/?subject=user',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

user_table_tag = 'user_table'
user_table_name = '用户列表'

extend_schema_tags(
    user_table_tag,
    user_table_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'get'
        }
    }
)