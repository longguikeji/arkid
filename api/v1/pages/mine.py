from openapi.utils import extend_schema_tags

tag = [ 
        'profile', 
        # 'third_part_account', 
        # 'subuser', 
        # 'user_token_manage',
        'user_application_account_manage',
        # "user_application_account_settings_manage"
    ]
path = 'mine'
name = '个人管理'

profile_tag = 'profile'
profile_name = '个人资料'

extend_schema_tags(
    profile_tag,
    profile_name,
    {
        'type':'description_page',
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

third_part_account_tag = 'third_part_account'
third_part_account_name = '第三方账号绑定'

extend_schema_tags(
    third_part_account_tag,
    third_part_account_name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/user/bind_info/',
            'method': 'get'
        }
    }
)

subuser_tag = 'subuser'
subuser_name = '子账号管理'

extend_schema_tags(
    subuser_tag,
    subuser_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/childaccounts/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'subuser.create',
                'description': '添加子账号',
                'icon': 'el-icon-plus',
            }
        },
        'local': {
            'switch': {
                'path': '/api/v1/childaccounts/{account_uuid}/check_type/',
                'method': 'get',
                'description': '切换为主账号',
                'icon': 'el-icon-switch-button'
            },
            'enter': {
                'path': '/api/v1/childaccounts/{account_uuid}/get_token/',
                'method': 'get',
                'description': '进入该账号',
                'icon': 'el-icon-position'
            },
            'delete': {
                'path': '/api/v1/childaccounts/{account_uuid}/detail/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

subuser_create_tag = 'subuser.create'
subuser_create_name = '添加子账号'

extend_schema_tags(
    subuser_create_tag,
    subuser_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/childaccounts/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/childaccounts/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

user_token_manage_tag = 'user_token_manage'
user_token_manage_name = 'Token管理'

extend_schema_tags(
    user_token_manage_tag,
    user_token_manage_name,
    {
        'type': 'description_page',
        'global': {
            'token': {
                'path': '/api/v1/user/token_expire/',
                'method': 'get',
                'description': '重置Token'
            }
        }
    }
)

user_application_account_tag = 'user_application_account_manage'
user_application_account_name = '应用内账号管理'

extend_schema_tags(
    user_application_account_tag,
    user_application_account_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account/',
            'method': 'get'
        },
        'local': {
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        },
        'global': {
            'create': {
                'tag': 'user_application_account_manage.create',
                'description': '创建新应用内账号',
                'icon': 'el-icon-plus'
            }
        }
    }
)

user_application_account_manage_create_tag = 'user_application_account_manage.create'
user_application_account_manage_create_name = '创建新应用内账号'

extend_schema_tags(
    user_application_account_manage_create_tag,
    user_application_account_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account/auth_from_third_platform/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account/auth_from_third_platform/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)


user_application_account_settings_tag = 'user_application_account_settings_manage'
user_application_account_settings_name = '应用内账号设置'

extend_schema_tags(
    user_application_account_settings_tag,
    user_application_account_settings_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account_settings/',
            'method': 'get'
        },
        'local': {
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account_settings/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        },
        'global': {
            'create': {
                'tag': 'user_application_account_settings_manage.create',
                'description': '创建新应用内账号设置',
                'icon': 'el-icon-plus'
            }
        }
    }
)

user_application_account_settings_manage_create_tag = 'user_application_account_settings_manage.create'
user_application_account_settings_manage_create_name = '创建新应用内账号设置'

extend_schema_tags(
    user_application_account_settings_manage_create_tag,
    user_application_account_settings_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account_settings/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user_application_account_settings/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)
