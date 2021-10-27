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
                'description': '添加用户',
                'icon': 'el-icon-plus'
            },
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                'method': 'get',
                'description': '全部导出',
                'icon': 'el-icon-download'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                'method': 'post',
                'description': '导入',
                'icon': 'el-icon-upload2'
            },
            'custom': {
                'tag': 'custom_fields',
                'description': '自定义字段',
                'icon': 'el-icon-document-add'
            }
        },
        'local': {
            'password': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                    'method': 'get',
                    'description': '设置密码',
                    'icon': 'el-icon-lock'
                },
                'write': {
                    'path': '/api/v1/user/reset_password/',
                    'method': 'post',
                    'description': '设置密码',
                    'icon': 'el-icon-lock'
                }
            },
            'update': {
                'tag': 'user.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
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

user_custom_fields_tag = 'custom_fields'
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
                'tag': 'custom_fields.create',
                'description': '添加自定义字段',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'custom_fields.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/config/custom_field/{id}/?subject=user',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

user_custom_fields_create_tag = 'custom_fields.create'
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

user_custom_fields_update_tag = 'custom_fields.update'
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