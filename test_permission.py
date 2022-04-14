import os
import uuid
import django
import requests
import collections

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()

from inventory.models import(
    Permission, User, UserTenantPermissionAndPermissionGroup,
    PermissionGroup, UserAppPermissionResult,
)
from oauth2_provider.models import get_application_model, get_access_token_model
from app.models import App

Application = get_application_model()
AccessToken = get_access_token_model()

def by_app_client_id_update_permission(client_id):
    '''
    根据client_id更新所有权限和权限分组，并更新所有的用户权限
    '''
    apps = App.valid_objects.filter(
        type__in=['OIDC-Platform']
    )
    for app_temp in apps:
        ## 更新缓存的权限
        data = app_temp.data
        app_client_id = data.get('client_id', '')
        if app_client_id == client_id:
            openapi_uris = data.get('openapi_uris', '')
            # 处理任务
            if openapi_uris:
                ## 重新更新openapi对应的权限
                app_permission_task(app_temp, openapi_uris)
                ## 重新计算所有用户权限
                app_all_user_permission(app_temp, client_id)
                break

def app_all_user_permission(app_temp, client_id):
    tenant = app_temp.tenant
    # 取得当前应用的所有用户权限
    application = Application.objects.filter(
        client_id=client_id 
    ).first()
    if application:
        auth_users = []
        # 分出所有的用户
        access_tokens = AccessToken.objects.filter(
            application=application,
        )
        for access_token in access_tokens:
            access_token_user = access_token.user
            if access_token_user not in auth_users:
                auth_users.append(access_token_user)
        # 取出所有的权限
        data_dict = {}
        permissions = Permission.valid_objects.filter(
            tenant=tenant,
            app=app_temp,
            content_type=None,
            permission_category='API',
            is_system_permission=True,
            base_code=app_temp.name,
        )
        for permission in permissions:
            if permission.sort_id != -1:
                data_dict[permission.sort_id] = permission
        # 取出所有的权限分组
        permissiongroups = PermissionGroup.valid_objects.filter(
            title=app_temp.name,
            tenant=tenant,
            app=app_temp,
            is_system_group=True,
            base_code=app_temp.name,
            is_update=True,
            parent__isnull=False,
        )
        for permissiongroup in permissiongroups:
            data_dict[permissiongroup.sort_id] = permissiongroup
        # 对数据进行一次排序
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
        # 将符合条件的数据进行重新组合
        user_permission_groups = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
            tenant=tenant,
            user__in=auth_users,
        )
        user_permission_info_dict = {}
        user_permission_group_info_dict = {}
        for user_permission_group in user_permission_groups:
            user_id = user_permission_group.user.id
            if user_permission_group.permission:
                if user_id not in user_permission_info_dict.keys():
                    user_permission_info_dict[user_id] = []
                permission_info_arr = user_permission_info_dict[user_id]
                permission_info_arr.append(user_permission_group.permission_id)
                user_permission_info_dict[user_id] = permission_info_arr
            else:
                if user_id not in user_permission_group_info_dict.keys():
                    user_permission_group_info_dict[user_id] = []
                permission_group_info_arr = user_permission_group_info_dict[user_id]
                permission_group_info_arr.append(user_permission_group.permissiongroup_id)
                user_permission_group_info_dict[user_id] = permission_group_info_arr
        # 旧用户app权限
        UserAppPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=app_temp,
        ).update(is_update=False)
        # 计算用户权限和权限分组
        for auth_user in auth_users:
            auth_user_id = auth_user.id
            user_permission_item_dict = user_permission_info_dict.get(auth_user_id, [])
            user_permission_group_item_dict = user_permission_group_info_dict.get(auth_user_id, [])
            result_str = ''
            for data_item in data_dict.values():
                if auth_user.is_superuser:
                    data_item.is_pass = 1
                else:
                    data_item_id = data_item.id
                    if isinstance(data_item, Permission):
                        # 权限
                        if data_item_id in user_permission_item_dict:
                            data_item.is_pass = 1
                        else:
                            if hasattr(data_item, 'is_pass') == False:
                                data_item.is_pass = 0
                    else:
                        # 权限分组
                        # 如果用户对某一个权限分组有权限，则对该权限分组内的所有权限有权限
                        if data_item.name == 'normal-user':
                            '''
                            普通用户
                            '''
                            data_item.is_pass = 1
                            container = data_item.container
                            if container:
                                for item in container:
                                    data_dict.get(item).is_pass = 1
                        elif data_item.name == 'platform-user' and auth_user.is_platform_user is True:
                            '''
                            平台用户
                            '''
                            data_item.is_pass = 1
                            container = data_item.container
                            if container:
                                for item in container:
                                    data_dict.get(item).is_pass = 1
                        elif data_item.name == 'tenant-user' and auth_user.tenants.filter(id=app_temp.tenant.id).exists() is True:
                            '''
                            租户用户
                            '''
                            data_item.is_pass = 1
                            container = data_item.container
                            if container:
                                for item in container:
                                    data_dict.get(item).is_pass = 1
                        elif data_item_id in user_permission_group_item_dict:
                            '''
                            其它分组
                            '''
                            data_item.is_pass = 1
                            container = data_item.container
                            if container:
                                for item in container:
                                    data_dict.get(item).is_pass = 1
                        else:
                            data_item.is_pass = 0
            for data_item in data_dict.values():
                result_str = result_str + str(data_item.is_pass)
            # 用户app权限结果
            userapppermissionresult, is_create = UserAppPermissionResult.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                app=app_temp,
                user=auth_user,
            )
            userapppermissionresult.is_update = True
            userapppermissionresult.result = result_str
            userapppermissionresult.save()
        UserAppPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=app_temp,
            is_update=False,
        ).delete()


def update_user_apppermission(client_id, user_id):
    '''
    更新单个用户的权限
    '''
    user = User.valid_objects.filter(id=user_id).first()
    apps = App.valid_objects.filter(
        type__in=['OIDC-Platform']
    )
    for app_temp in apps:
        ## 更新缓存的权限
        data = app_temp.data
        app_client_id = data.get('client_id', '')
        if app_client_id == client_id:
            openapi_uris = data.get('openapi_uris', '')
            # 处理任务
            if openapi_uris:
                update_single_user_apppermission(app_temp, user, client_id)
            break

def update_single_user_apppermission(app_temp, user, client_id):
    tenant = app_temp.tenant
    # 取出所有的权限
    data_dict = {}
    permissions = Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=app_temp.name,
    )
    for permission in permissions:
        if permission.sort_id != -1:
            data_dict[permission.sort_id] = permission
    # 取出所有的权限分组
    permissiongroups = PermissionGroup.valid_objects.filter(
        title=app_temp.name,
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        base_code=app_temp.name,
        is_update=True,
        parent__isnull=False,
    )
    for permissiongroup in permissiongroups:
        data_dict[permissiongroup.sort_id] = permissiongroup
    # 对数据进行一次排序
    data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
    # 将符合条件的数据进行重新组合
    user_permission_groups = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
        tenant=tenant,
        user=user,
    )
    user_permission_info_dict = {}
    user_permission_group_info_dict = {}
    for user_permission_group in user_permission_groups:
        user_id = user_permission_group.user.id
        if user_permission_group.permission:
            if user_id not in user_permission_info_dict.keys():
                user_permission_info_dict[user_id] = []
            permission_info_arr = user_permission_info_dict[user_id]
            permission_info_arr.append(user_permission_group.permission_id)
            user_permission_info_dict[user_id] = permission_info_arr
        else:
            if user_id not in user_permission_group_info_dict.keys():
                user_permission_group_info_dict[user_id] = []
            permission_group_info_arr = user_permission_group_info_dict[user_id]
            permission_group_info_arr.append(user_permission_group.permissiongroup_id)
            user_permission_group_info_dict[user_id] = permission_group_info_arr
    # 计算用户权限和权限分组
    auth_user = user
    auth_user_id = auth_user.id
    user_permission_item_dict = user_permission_info_dict.get(auth_user_id, [])
    user_permission_group_item_dict = user_permission_group_info_dict.get(auth_user_id, [])
    result_str = ''
    for data_item in data_dict.values():
        if auth_user.is_superuser:
            data_item.is_pass = 1
        else:
            data_item_id = data_item.id
            if isinstance(data_item, Permission):
                # 权限
                if data_item_id in user_permission_item_dict:
                    data_item.is_pass = 1
                else:
                    if hasattr(data_item, 'is_pass') == False:
                        data_item.is_pass = 0
            else:
                # 权限分组
                # 如果用户对某一个权限分组有权限，则对该权限分组内的所有权限有权限
                if data_item.name == 'normal-user':
                    '''
                    普通用户
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                elif data_item.name == 'platform-user' and auth_user.is_platform_user is True:
                    '''
                    平台用户
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                elif data_item.name == 'tenant-user' and auth_user.tenants.filter(id=app_temp.tenant.id).exists() is True:
                    '''
                    租户用户
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                elif data_item_id in user_permission_group_item_dict:
                    '''
                    其它分组
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                else:
                    data_item.is_pass = 0
    for data_item in data_dict.values():
        result_str = result_str + str(data_item.is_pass)
    # 用户app权限结果
    userapppermissionresult, is_create = UserAppPermissionResult.objects.get_or_create(
        is_del=False,
        tenant=tenant,
        app=app_temp,
        user=auth_user,
    )
    userapppermissionresult.is_update = True
    userapppermissionresult.result = result_str
    userapppermissionresult.save()

def app_permission_task(app_temp, api_info):
    # response = requests.get(api_info)
    # response = response.json()
    response = {
        "openapi":"3.0.2",
        "info":{
            "title":"NinjaAPI",
            "version":"1.0.0",
            "description":""
        },
        "paths":{
            "/api/v1/login":{
                "get":{
                    "operationId":"app_auth_login",
                    "summary":"Login",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"state",
                            "schema":{
                                "title":"State",
                                "default":"browser",
                                "type":"string"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"tenant_slug",
                            "schema":{
                                "title":"Tenant Slug",
                                "type":"string"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"token",
                            "schema":{
                                "title":"Token",
                                "type":"string"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    }
                }
            },
            "/api/v1/callback":{
                "get":{
                    "operationId":"app_auth_callback",
                    "summary":"Callback",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"code",
                            "schema":{
                                "title":"Code",
                                "type":"string"
                            },
                            "required":True
                        },
                        {
                            "in":"query",
                            "name":"state",
                            "schema":{
                                "title":"State",
                                "type":"string"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    }
                }
            },
            "/api/v1/upload_file":{
                "post":{
                    "operationId":"app_file_upload_file",
                    "summary":"Upload File",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "description":"\u4e0a\u4f20zip\u5305",
                    "requestBody":{
                        "content":{
                            "multipart/form-data":{
                                "schema":{
                                    "title":"FileParams",
                                    "type":"object",
                                    "properties":{
                                        "file":{
                                            "title":"File",
                                            "type":"string",
                                            "format":"binary"
                                        }
                                    },
                                    "required":[
                                        "file"
                                    ]
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/upload_github":{
                "get":{
                    "operationId":"app_file_upload_github",
                    "summary":"Upload Github",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"state",
                            "schema":{
                                "title":"State",
                                "type":"string"
                            },
                            "required":True
                        },
                        {
                            "in":"query",
                            "name":"github_repo",
                            "schema":{
                                "title":"Github Repo",
                                "type":"string"
                            },
                            "required":True
                        },
                        {
                            "in":"query",
                            "name":"branch",
                            "schema":{
                                "title":"Branch",
                                "default":"main",
                                "type":"string"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "description":"\u901a\u8fc7github\u4ed3\u5e93\u94fe\u63a5\u4e0a\u4f20",
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/upload_github_callback":{
                "get":{
                    "operationId":"app_file_upload_github_callback",
                    "summary":"Upload Github Callback",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"code",
                            "schema":{
                                "title":"Code",
                                "type":"string"
                            },
                            "required":True
                        },
                        {
                            "in":"query",
                            "name":"state",
                            "schema":{
                                "title":"State",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "description":"\u901a\u8fc7github\u4ed3\u5e93\u94fe\u63a5\u4e0a\u4f20"
                }
            },
            "/api/v1/upload_github_status":{
                "get":{
                    "operationId":"app_file_upload_github_status",
                    "summary":"Upload Github Status",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"state",
                            "schema":{
                                "title":"State",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "description":"\u83b7\u53d6github\u4ed3\u5e93clone\u5230\u672c\u5730\u662f\u5426\u6210\u529f",
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/download/{file_uuid}":{
                "get":{
                    "operationId":"app_file_download",
                    "summary":"Download",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"file_uuid",
                            "schema":{
                                "title":"File Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/extensions":{
                "post":{
                    "operationId":"app_extension_create_extension",
                    "summary":"Create Extension",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/ExtensionIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_extension_list_extensions",
                    "summary":"List Extensions",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"status",
                            "schema":{
                                "title":"Status",
                                "type":"string"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedExtensionOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/extensions/{extension_uuid}":{
                "get":{
                    "operationId":"app_extension_get_extension",
                    "summary":"Get Extension",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ExtensionDetailOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "put":{
                    "operationId":"app_extension_update_extension",
                    "summary":"Update Extension",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/ExtensionIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "delete":{
                    "operationId":"app_extension_delete_extension",
                    "summary":"Delete Extension",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/extensions/{extension_uuid}/submit":{
                "get":{
                    "operationId":"app_extension_create_review",
                    "summary":"Create Review",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/arkstore/extensions":{
                "get":{
                    "operationId":"app_extension_list_on_shelve_extensions",
                    "summary":"List On Shelve Extensions",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"purchased",
                            "schema":{
                                "title":"Purchased",
                                "type":"boolean"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedOnShelveExtensionOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/arkstore/extensions/{extension_uuid}":{
                "get":{
                    "operationId":"app_extension_get_on_shelve_extension",
                    "summary":"Get On Shelve Extension",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ExtensionOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/arkstore/extensions/{extension_uuid}/download":{
                "get":{
                    "operationId":"app_extension_download_extension",
                    "summary":"Download Extension",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/user/orders":{
                "post":{
                    "operationId":"app_order_create_order",
                    "summary":"Create Order",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/OrderIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_order_user_orders_list",
                    "summary":"User Orders List",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"status",
                            "schema":{
                                "default":"",
                                "allOf":[
                                    {
                                        "title":"OrderState",
                                        "description":"An enumeration.",
                                        "enum":[
                                            "created",
                                            "deleted",
                                            "payed"
                                        ],
                                        "type":"string"
                                    }
                                ]
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedOrderOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/user/orders/{order_no}":{
                "put":{
                    "operationId":"app_order_user_orders_update",
                    "summary":"User Orders Update",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"order_no",
                            "schema":{
                                "title":"Order No",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/OrderOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/OrderIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_order_user_orders_detail",
                    "summary":"User Orders Detail",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"order_no",
                            "schema":{
                                "title":"Order No",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/OrderOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "delete":{
                    "operationId":"app_order_user_orders_delete",
                    "summary":"User Orders Delete",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"order_no",
                            "schema":{
                                "title":"Order No",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/agent/orders":{
                "get":{
                    "operationId":"app_order_list_agent_orders",
                    "summary":"List Agent Orders",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"status",
                            "schema":{
                                "default":"",
                                "allOf":[
                                    {
                                        "title":"OrderState",
                                        "description":"An enumeration.",
                                        "enum":[
                                            "created",
                                            "deleted",
                                            "payed"
                                        ],
                                        "type":"string"
                                    }
                                ]
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedOrderOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/developer/orders":{
                "get":{
                    "operationId":"app_order_list_developer_orders",
                    "summary":"List Developer Orders",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"status",
                            "schema":{
                                "default":"",
                                "allOf":[
                                    {
                                        "title":"OrderState",
                                        "description":"An enumeration.",
                                        "enum":[
                                            "created",
                                            "deleted",
                                            "payed"
                                        ],
                                        "type":"string"
                                    }
                                ]
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedOrderOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/orders":{
                "get":{
                    "operationId":"app_order_list_all_orders",
                    "summary":"List All Orders",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"status",
                            "schema":{
                                "default":"",
                                "allOf":[
                                    {
                                        "title":"OrderState",
                                        "description":"An enumeration.",
                                        "enum":[
                                            "created",
                                            "deleted",
                                            "payed"
                                        ],
                                        "type":"string"
                                    }
                                ]
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedOrderOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/orders/{order_no}":{
                "get":{
                    "operationId":"app_order_get_order_detail",
                    "summary":"Get Order Detail",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"order_no",
                            "schema":{
                                "title":"Order No",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/OrderOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "delete":{
                    "operationId":"app_order_delete_order",
                    "summary":"Delete Order",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"order_no",
                            "schema":{
                                "title":"Order No",
                                "type":"integer"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/pay/notify":{
                "post":{
                    "operationId":"app_order_pay_notify",
                    "summary":"Pay Notify",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    }
                }
            },
            "/api/v1/categories":{
                "post":{
                    "operationId":"app_category_create_category",
                    "summary":"Create Category",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/CategoryIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_category_list_categories",
                    "summary":"List Categories",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "title":"Response",
                                        "type":"array",
                                        "items":{
                                            "$ref":"#/components/schemas/CategoryOut"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/categories/{category_uuid}":{
                "get":{
                    "operationId":"app_category_get_category",
                    "summary":"Get Category",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"category_uuid",
                            "schema":{
                                "title":"Category Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/CategoryOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "put":{
                    "operationId":"app_category_update_category",
                    "summary":"Update Category",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"category_uuid",
                            "schema":{
                                "title":"Category Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/CategoryIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "delete":{
                    "operationId":"app_category_delete_category",
                    "summary":"Delete Category",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"category_uuid",
                            "schema":{
                                "title":"Category Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/extensions/{extension_uuid}/reviews/{action}":{
                "post":{
                    "operationId":"app_review_create_review",
                    "summary":"Create Review",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        },
                        {
                            "in":"path",
                            "name":"action",
                            "schema":{
                                "title":"Action",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/ReviewIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/reviews/{review_uuid}":{
                "get":{
                    "operationId":"app_review_get_review",
                    "summary":"Get Review",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"review_uuid",
                            "schema":{
                                "title":"Review Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ReviewOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/reviews":{
                "get":{
                    "operationId":"app_review_list_reviews",
                    "summary":"List Reviews",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "title":"Response",
                                        "type":"array",
                                        "items":{
                                            "$ref":"#/components/schemas/ReviewOut"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/extensions/{extension_uuid}/review":{
                "get":{
                    "operationId":"app_review_get_extension_first_review",
                    "summary":"Get Extension First Review",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"extension_uuid",
                            "schema":{
                                "title":"Extension Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ReviewMsgOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/userinfo":{
                "get":{
                    "operationId":"app_user_userinfo",
                    "summary":"Userinfo",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/UserOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/bind_agent":{
                "post":{
                    "operationId":"app_agent_bind_agent",
                    "summary":"Bind Agent",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/Message"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/BindAgentIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_agent_bind_info",
                    "summary":"Bind Info",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentOut"
                                    }
                                }
                            }
                        },
                        "204":{
                            "description":"No Content"
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/BindAgentIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/agent_notice":{
                "post":{
                    "operationId":"app_agent_create_agent_notice",
                    "summary":"Create Agent Notice",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentNoticeSchema"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/AgentNoticeSchema"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_agent_agent_notice_detail",
                    "summary":"Agent Notice Detail",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentNoticeSchema"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/agent_info":{
                "get":{
                    "operationId":"app_agent_agent_info",
                    "summary":"Agent Info",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentInfo"
                                    }
                                }
                            }
                        },
                        "204":{
                            "description":"No Content"
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/agents":{
                "get":{
                    "operationId":"app_agent_agent_list",
                    "summary":"Agent List",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedAgentOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/agent_grade":{
                "get":{
                    "operationId":"app_agent_agent_grade_list",
                    "summary":"Agent Grade List",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedAgentGradeOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "post":{
                    "operationId":"app_agent_agent_grade_create",
                    "summary":"Agent Grade Create",
                    "parameters":[

                    ],
                    "responses":{
                        "201":{
                            "description":"Created",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentGradeOut"
                                    }
                                }
                            }
                        },
                        "400":{
                            "description":"Bad Request",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/AgentGradeIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/agent_grade/{uuid}":{
                "post":{
                    "operationId":"app_agent_agent_grade_update",
                    "summary":"Agent Grade Update",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"uuid",
                            "schema":{
                                "title":"Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentGradeOut"
                                    }
                                }
                            }
                        },
                        "416":{
                            "description":"Requested Range Not Satisfiable",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "418":{
                            "description":"Unknown Status Code",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "451":{
                            "description":"Unavailable For Legal Reasons",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "425":{
                            "description":"Unknown Status Code",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "429":{
                            "description":"Too Many Requests",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "400":{
                            "description":"Bad Request",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "401":{
                            "description":"Unauthorized",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "402":{
                            "description":"Payment Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "403":{
                            "description":"Forbidden",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "405":{
                            "description":"Method Not Allowed",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "406":{
                            "description":"Not Acceptable",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "407":{
                            "description":"Proxy Authentication Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "408":{
                            "description":"Request Timeout",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "409":{
                            "description":"Conflict",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "410":{
                            "description":"Gone",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "411":{
                            "description":"Length Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "412":{
                            "description":"Precondition Failed",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/AgentGradeIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_agent_agent_grade_detail",
                    "summary":"Agent Grade Detail",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"uuid",
                            "schema":{
                                "title":"Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/AgentGradeOut"
                                    }
                                }
                            }
                        },
                        "416":{
                            "description":"Requested Range Not Satisfiable",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "418":{
                            "description":"Unknown Status Code",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "451":{
                            "description":"Unavailable For Legal Reasons",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "425":{
                            "description":"Unknown Status Code",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "429":{
                            "description":"Too Many Requests",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "400":{
                            "description":"Bad Request",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "401":{
                            "description":"Unauthorized",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "402":{
                            "description":"Payment Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "403":{
                            "description":"Forbidden",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "405":{
                            "description":"Method Not Allowed",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "406":{
                            "description":"Not Acceptable",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "407":{
                            "description":"Proxy Authentication Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "408":{
                            "description":"Request Timeout",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "409":{
                            "description":"Conflict",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "410":{
                            "description":"Gone",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "411":{
                            "description":"Length Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "412":{
                            "description":"Precondition Failed",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "delete":{
                    "operationId":"app_agent_agent_grade_delete",
                    "summary":"Agent Grade Delete",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"uuid",
                            "schema":{
                                "title":"Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "416":{
                            "description":"Requested Range Not Satisfiable",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "418":{
                            "description":"Unknown Status Code",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "451":{
                            "description":"Unavailable For Legal Reasons",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "425":{
                            "description":"Unknown Status Code",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "429":{
                            "description":"Too Many Requests",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "400":{
                            "description":"Bad Request",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "401":{
                            "description":"Unauthorized",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "402":{
                            "description":"Payment Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "403":{
                            "description":"Forbidden",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "405":{
                            "description":"Method Not Allowed",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "406":{
                            "description":"Not Acceptable",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "407":{
                            "description":"Proxy Authentication Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "408":{
                            "description":"Request Timeout",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "409":{
                            "description":"Conflict",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "410":{
                            "description":"Gone",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "411":{
                            "description":"Length Required",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "412":{
                            "description":"Precondition Failed",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/income/agent":{
                "get":{
                    "operationId":"app_income_agent_income",
                    "summary":"Agent Income",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/TotalIncomeOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/income/agent/detail":{
                "get":{
                    "operationId":"app_income_agent_income_detail",
                    "summary":"Agent Income Detail",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedIncomeDetailOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/income/developer":{
                "get":{
                    "operationId":"app_income_developer_income",
                    "summary":"Developer Income",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/TotalIncomeOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/income/developer/detail":{
                "get":{
                    "operationId":"app_income_developer_income_detail",
                    "summary":"Developer Income Detail",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "title":"Response",
                                        "type":"array",
                                        "items":{
                                            "$ref":"#/components/schemas/IncomeDetailOut"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/income/platform":{
                "get":{
                    "operationId":"app_income_platform_income",
                    "summary":"Platform Income",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PlatformIncomeOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/withdraw":{
                "post":{
                    "operationId":"app_withdraw_create_withdraw",
                    "summary":"Create Withdraw",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/WithdrawOut"
                                    }
                                }
                            }
                        },
                        "400":{
                            "description":"Bad Request",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/WithdrawIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_withdraw_list_withdraw",
                    "summary":"List Withdraw",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedWithdrawOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/withdraw/{withdraw_uuid}":{
                "get":{
                    "operationId":"app_withdraw_withdraw_detail",
                    "summary":"Withdraw Detail",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"withdraw_uuid",
                            "schema":{
                                "title":"Withdraw Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/WithdrawOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "post":{
                    "operationId":"app_withdraw_withdraw_action",
                    "summary":"Withdraw Action",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"withdraw_uuid",
                            "schema":{
                                "title":"Withdraw Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/WithdrawOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/WithdrawAction"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/rebate":{
                "post":{
                    "operationId":"app_rebate_create_rebate",
                    "summary":"Create Rebate",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/RebateOut"
                                    }
                                }
                            }
                        },
                        "400":{
                            "description":"Bad Request",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/RebateIn"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_rebate_list_rebate",
                    "summary":"List Rebate",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedRebateOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/rebate/{rebate_uuid}":{
                "get":{
                    "operationId":"app_rebate_rebate_detail",
                    "summary":"Rebate Detail",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"rebate_uuid",
                            "schema":{
                                "title":"Rebate Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/RebateOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "delete":{
                    "operationId":"app_rebate_rebate_delete",
                    "summary":"Rebate Delete",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"rebate_uuid",
                            "schema":{
                                "title":"Rebate Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "post":{
                    "operationId":"app_rebate_rebate_action",
                    "summary":"Rebate Action",
                    "parameters":[
                        {
                            "in":"path",
                            "name":"rebate_uuid",
                            "schema":{
                                "title":"Rebate Uuid",
                                "type":"string"
                            },
                            "required":True
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/RebateOut"
                                    }
                                }
                            }
                        },
                        "404":{
                            "description":"Not Found",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/ErrorMsg"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/RebateAction"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/developer_notice":{
                "post":{
                    "operationId":"app_developer_create_developer_notice",
                    "summary":"Create Developer Notice",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/DeveloperNoticeSchema"
                                    }
                                }
                            }
                        }
                    },
                    "requestBody":{
                        "content":{
                            "application/json":{
                                "schema":{
                                    "$ref":"#/components/schemas/DeveloperNoticeSchema"
                                }
                            }
                        },
                        "required":True
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                },
                "get":{
                    "operationId":"app_developer_developer_notice_detail",
                    "summary":"Developer Notice Detail",
                    "parameters":[

                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/DeveloperNoticeSchema"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            },
            "/api/v1/developers":{
                "get":{
                    "operationId":"app_developer_developer_list",
                    "summary":"Developer List",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"limit",
                            "schema":{
                                "title":"Limit",
                                "default":100,
                                "exclusiveMinimum":0,
                                "type":"integer"
                            },
                            "required":False
                        },
                        {
                            "in":"query",
                            "name":"offset",
                            "schema":{
                                "title":"Offset",
                                "default":0,
                                "exclusiveMinimum":-1,
                                "type":"integer"
                            },
                            "required":False
                        }
                    ],
                    "responses":{
                        "200":{
                            "description":"OK",
                            "content":{
                                "application/json":{
                                    "schema":{
                                        "$ref":"#/components/schemas/PagedDeveloperOut"
                                    }
                                }
                            }
                        }
                    },
                    "security":[
                        {
                            "GlobalAuth":[

                            ]
                        }
                    ]
                }
            }
        },
        "components":{
            "schemas":{
                "ExtensionIn":{
                    "title":"ExtensionIn",
                    "type":"object",
                    "properties":{
                        "name":{
                            "title":"Name",
                            "type":"string"
                        },
                        "package_idendifer":{
                            "title":"Package Idendifer",
                            "type":"string"
                        },
                        "author":{
                            "title":"Author",
                            "type":"string"
                        },
                        "logo":{
                            "title":"Logo",
                            "type":"string"
                        },
                        "description":{
                            "title":"Description",
                            "type":"string"
                        },
                        "categories":{
                            "title":"Categories",
                            "type":"array",
                            "items":{
                                "type":"string"
                            }
                        },
                        "labels":{
                            "title":"Labels",
                            "type":"array",
                            "items":{
                                "type":"string"
                            }
                        },
                        "price":{
                            "title":"Price",
                            "type":"number"
                        },
                        "cost_discount":{
                            "title":"Cost Discount",
                            "type":"number"
                        },
                        "price_type":{
                            "title":"Price Type",
                            "type":"string"
                        },
                        "file_name":{
                            "title":"File Name",
                            "type":"string"
                        }
                    },
                    "required":[
                        "name",
                        "package_idendifer",
                        "author",
                        "description",
                        "price",
                        "cost_discount",
                        "price_type",
                        "file_name"
                    ]
                },
                "ExtensionOut":{
                    "title":"ExtensionOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string",
                            "format":"uuid"
                        },
                        "name":{
                            "title":"Name",
                            "maxLength":128,
                            "type":"string"
                        },
                        "package_idendifer":{
                            "title":"Package Idendifer",
                            "maxLength":128,
                            "type":"string"
                        },
                        "author":{
                            "title":"Author",
                            "maxLength":128,
                            "type":"string"
                        },
                        "logo":{
                            "title":"Logo",
                            "default":"",
                            "maxLength":1024,
                            "type":"string"
                        },
                        "description":{
                            "title":"Description",
                            "type":"string"
                        },
                        "labels":{
                            "title":"\u63d2\u4ef6\u6807\u7b7e",
                            "default":"",
                            "maxLength":1024,
                            "type":"string"
                        },
                        "status":{
                            "title":"\u63d2\u4ef6\u72b6\u6001",
                            "default":"created",
                            "maxLength":128,
                            "type":"string"
                        },
                        "created":{
                            "title":"\u521b\u5efa\u65f6\u95f4",
                            "type":"string",
                            "format":"date-time"
                        },
                        "categories":{
                            "title":"Categories",
                            "type":"string"
                        }
                    },
                    "required":[
                        "name",
                        "package_idendifer",
                        "categories"
                    ]
                },
                "PagedExtensionOut":{
                    "title":"PagedExtensionOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/ExtensionOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "ExtensionDetailOut":{
                    "title":"ExtensionDetailOut",
                    "type":"object",
                    "properties":{
                        "name":{
                            "title":"Name",
                            "maxLength":128,
                            "type":"string"
                        },
                        "package_idendifer":{
                            "title":"Package Idendifer",
                            "maxLength":128,
                            "type":"string"
                        },
                        "author":{
                            "title":"Author",
                            "maxLength":128,
                            "type":"string"
                        },
                        "logo":{
                            "title":"Logo",
                            "default":"",
                            "maxLength":1024,
                            "type":"string"
                        },
                        "description":{
                            "title":"Description",
                            "type":"string"
                        },
                        "categories":{
                            "title":"\u63d2\u4ef6\u7c7b\u522b",
                            "type":"array",
                            "items":{
                                "type":"integer"
                            }
                        },
                        "labels":{
                            "title":"\u63d2\u4ef6\u6807\u7b7e",
                            "default":"",
                            "maxLength":1024,
                            "type":"string"
                        }
                    },
                    "required":[
                        "name",
                        "package_idendifer",
                        "categories"
                    ]
                },
                "OnShelveExtensionOut":{
                    "title":"OnShelveExtensionOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string",
                            "format":"uuid"
                        },
                        "name":{
                            "title":"Name",
                            "maxLength":128,
                            "type":"string"
                        },
                        "package_idendifer":{
                            "title":"Package Idendifer",
                            "maxLength":128,
                            "type":"string"
                        },
                        "author":{
                            "title":"Author",
                            "maxLength":128,
                            "type":"string"
                        },
                        "logo":{
                            "title":"Logo",
                            "default":"",
                            "maxLength":1024,
                            "type":"string"
                        },
                        "description":{
                            "title":"Description",
                            "type":"string"
                        },
                        "labels":{
                            "title":"\u63d2\u4ef6\u6807\u7b7e",
                            "default":"",
                            "maxLength":1024,
                            "type":"string"
                        },
                        "status":{
                            "title":"\u63d2\u4ef6\u72b6\u6001",
                            "default":"created",
                            "maxLength":128,
                            "type":"string"
                        },
                        "created":{
                            "title":"\u521b\u5efa\u65f6\u95f4",
                            "type":"string",
                            "format":"date-time"
                        },
                        "categories":{
                            "title":"Categories",
                            "type":"string"
                        },
                        "purchased":{
                            "title":"Purchased",
                            "type":"boolean"
                        }
                    },
                    "required":[
                        "name",
                        "package_idendifer",
                        "categories",
                        "purchased"
                    ]
                },
                "PagedOnShelveExtensionOut":{
                    "title":"PagedOnShelveExtensionOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/OnShelveExtensionOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "OrderIn":{
                    "title":"OrderIn",
                    "type":"object",
                    "properties":{
                        "price_mode_uuid":{
                            "title":"Price Mode Uuid",
                            "type":"string"
                        },
                        "extension_uuid":{
                            "title":"Extension Uuid",
                            "type":"string"
                        },
                        "days_limit":{
                            "title":"Days Limit",
                            "type":"integer"
                        },
                        "users_limit":{
                            "title":"Users Limit",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "extension_uuid"
                    ]
                },
                "OrderOut":{
                    "title":"OrderOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string",
                            "format":"uuid"
                        },
                        "pay_time":{
                            "title":"\u652f\u4ed8\u65f6\u95f4",
                            "type":"string",
                            "format":"date-time"
                        },
                        "total_price":{
                            "title":"\u603b\u91d1\u989d",
                            "default":0,
                            "type":"number"
                        },
                        "status":{
                            "title":"\u63d2\u4ef6\u72b6\u6001",
                            "default":"created",
                            "maxLength":128,
                            "type":"string"
                        },
                        "transaction_id":{
                            "title":"\u6d41\u6c34\u53f7",
                            "default":"",
                            "maxLength":256,
                            "type":"string"
                        },
                        "days_limit":{
                            "title":"\u5929\u6570\u9650\u5236",
                            "default":0,
                            "type":"integer"
                        },
                        "users_limit":{
                            "title":"\u4eba\u6570\u9650\u5236",
                            "default":0,
                            "type":"integer"
                        }
                    }
                },
                "PagedOrderOut":{
                    "title":"PagedOrderOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/OrderOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "ErrorMsg":{
                    "title":"ErrorMsg",
                    "type":"object",
                    "properties":{
                        "code":{
                            "title":"Code",
                            "type":"string"
                        },
                        "msg":{
                            "title":"Msg",
                            "type":"string"
                        }
                    },
                    "required":[
                        "code",
                        "msg"
                    ]
                },
                "CategoryIn":{
                    "title":"CategoryIn",
                    "type":"object",
                    "properties":{
                        "name":{
                            "title":"Name",
                            "type":"string"
                        }
                    },
                    "required":[
                        "name"
                    ]
                },
                "CategoryOut":{
                    "title":"CategoryOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string",
                            "format":"uuid"
                        },
                        "name":{
                            "title":"Name",
                            "maxLength":128,
                            "type":"string"
                        }
                    },
                    "required":[
                        "name"
                    ]
                },
                "ReviewIn":{
                    "title":"ReviewIn",
                    "type":"object",
                    "properties":{
                        "message":{
                            "title":"Message",
                            "format":"textarea",
                            "type":"string"
                        }
                    },
                    "required":[
                        "message"
                    ]
                },
                "ReviewOut":{
                    "title":"ReviewOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string",
                            "format":"uuid"
                        },
                        "action":{
                            "title":"\u63d2\u4ef6\u5ba1\u6838\u4e0e\u4e0a\u67b6",
                            "default":"approve",
                            "maxLength":128,
                            "type":"string"
                        },
                        "message":{
                            "title":"Message",
                            "type":"string"
                        },
                        "extension":{
                            "title":"Extension",
                            "type":"integer"
                        },
                        "user":{
                            "title":"User",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "extension",
                        "user"
                    ]
                },
                "ReviewMsgOut":{
                    "title":"ReviewMsgOut",
                    "type":"object",
                    "properties":{
                        "message":{
                            "title":"Message",
                            "type":"string"
                        }
                    }
                },
                "UserOut":{
                    "title":"UserOut",
                    "type":"object",
                    "properties":{
                        "user_uuid":{
                            "title":"User Uuid",
                            "type":"string",
                            "format":"uuid"
                        },
                        "username":{
                            "title":"Username",
                            "maxLength":128,
                            "type":"string"
                        },
                        "nickname":{
                            "title":"Nickname",
                            "maxLength":128,
                            "type":"string"
                        }
                    },
                    "required":[
                        "user_uuid",
                        "username"
                    ]
                },
                "Message":{
                    "title":"Message",
                    "type":"object",
                    "properties":{
                        "message":{
                            "title":"Message",
                            "type":"string"
                        }
                    },
                    "required":[
                        "message"
                    ]
                },
                "BindAgentIn":{
                    "title":"BindAgentIn",
                    "type":"object",
                    "properties":{
                        "tenant_slug":{
                            "title":"Tenant Slug",
                            "type":"string"
                        }
                    },
                    "required":[
                        "tenant_slug"
                    ]
                },
                "AgentOut":{
                    "title":"AgentOut",
                    "type":"object",
                    "properties":{
                        "tenant_uuid":{
                            "title":"Tenant Uuid",
                            "type":"string"
                        },
                        "tenant_slug":{
                            "title":"Tenant Slug",
                            "type":"string"
                        },
                        "total_sales":{
                            "title":"Total Sales",
                            "type":"number"
                        },
                        "agent_level":{
                            "title":"Agent Level",
                            "type":"integer"
                        },
                        "purchase_discount":{
                            "title":"Purchase Discount",
                            "type":"number"
                        },
                        "extra_discount":{
                            "title":"Extra Discount",
                            "type":"number"
                        }
                    },
                    "required":[
                        "tenant_uuid",
                        "tenant_slug",
                        "total_sales",
                        "agent_level",
                        "purchase_discount",
                        "extra_discount"
                    ]
                },
                "AgentNoticeSchema":{
                    "title":"AgentNoticeSchema",
                    "type":"object",
                    "properties":{
                        "notice":{
                            "title":"Notice",
                            "format":"md",
                            "type":"string"
                        }
                    },
                    "required":[
                        "notice"
                    ]
                },
                "AgentInfo":{
                    "title":"AgentInfo",
                    "type":"object",
                    "properties":{
                        "total_sales":{
                            "title":"Total Sales",
                            "type":"number"
                        },
                        "current_level":{
                            "title":"Current Level",
                            "type":"integer"
                        },
                        "current_discount":{
                            "title":"Current Discount",
                            "type":"number"
                        },
                        "next_level_required":{
                            "title":"Next Level Required",
                            "type":"number"
                        }
                    },
                    "required":[
                        "total_sales",
                        "current_level",
                        "current_discount",
                        "next_level_required"
                    ]
                },
                "PagedAgentOut":{
                    "title":"PagedAgentOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/AgentOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "AgentGradeOut":{
                    "title":"AgentGradeOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string"
                        },
                        "level":{
                            "title":"Level",
                            "type":"integer"
                        },
                        "total_sales":{
                            "title":"Total Sales",
                            "type":"number"
                        },
                        "purchase_discount":{
                            "title":"Purchase Discount",
                            "type":"number"
                        }
                    },
                    "required":[
                        "uuid",
                        "level",
                        "total_sales",
                        "purchase_discount"
                    ]
                },
                "PagedAgentGradeOut":{
                    "title":"PagedAgentGradeOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/AgentGradeOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "AgentGradeIn":{
                    "title":"AgentGradeIn",
                    "type":"object",
                    "properties":{
                        "level":{
                            "title":"Level",
                            "type":"integer"
                        },
                        "total_sales":{
                            "title":"Total Sales",
                            "type":"number"
                        },
                        "purchase_discount":{
                            "title":"Purchase Discount",
                            "type":"number"
                        }
                    },
                    "required":[
                        "level",
                        "total_sales",
                        "purchase_discount"
                    ]
                },
                "TotalIncomeOut":{
                    "title":"TotalIncomeOut",
                    "type":"object",
                    "properties":{
                        "total_income":{
                            "title":"Total Income",
                            "type":"number"
                        }
                    },
                    "required":[
                        "total_income"
                    ]
                },
                "IncomeDetailOut":{
                    "title":"IncomeDetailOut",
                    "type":"object",
                    "properties":{
                        "order_no":{
                            "title":"Order No",
                            "type":"string"
                        },
                        "change_amount":{
                            "title":"Change Amount",
                            "type":"number"
                        },
                        "remark":{
                            "title":"Remark",
                            "type":"string"
                        }
                    },
                    "required":[
                        "order_no",
                        "change_amount",
                        "remark"
                    ]
                },
                "PagedIncomeDetailOut":{
                    "title":"PagedIncomeDetailOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/IncomeDetailOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "PlatformIncomeOut":{
                    "title":"PlatformIncomeOut",
                    "type":"object",
                    "properties":{
                        "total_orders":{
                            "title":"Total Orders",
                            "type":"number"
                        },
                        "total_platform":{
                            "title":"Total Platform",
                            "type":"number"
                        },
                        "total_agent":{
                            "title":"Total Agent",
                            "type":"number"
                        },
                        "total_developer":{
                            "title":"Total Developer",
                            "type":"number"
                        }
                    },
                    "required":[
                        "total_orders",
                        "total_platform",
                        "total_agent",
                        "total_developer"
                    ]
                },
                "WithdrawOut":{
                    "title":"WithdrawOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string"
                        },
                        "amount":{
                            "title":"Amount",
                            "type":"number"
                        },
                        "from_wallet":{
                            "title":"From Wallet",
                            "type":"string"
                        },
                        "remark":{
                            "title":"Remark",
                            "format":"textarea",
                            "type":"string"
                        },
                        "status":{
                            "title":"Status",
                            "type":"string"
                        }
                    },
                    "required":[
                        "uuid",
                        "amount",
                        "from_wallet",
                        "remark",
                        "status"
                    ]
                },
                "WalletType":{
                    "title":"WalletType",
                    "description":"An enumeration.",
                    "enum":[
                        "agent",
                        "developer"
                    ],
                    "type":"string"
                },
                "WithdrawIn":{
                    "title":"WithdrawIn",
                    "type":"object",
                    "properties":{
                        "amount":{
                            "title":"Amount",
                            "type":"number"
                        },
                        "from_wallet":{
                            "$ref":"#/components/schemas/WalletType"
                        },
                        "remark":{
                            "title":"Remark",
                            "default":"",
                            "format":"textarea",
                            "type":"string"
                        }
                    },
                    "required":[
                        "amount",
                        "from_wallet"
                    ]
                },
                "PagedWithdrawOut":{
                    "title":"PagedWithdrawOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/WithdrawOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "ActionType":{
                    "title":"ActionType",
                    "description":"An enumeration.",
                    "enum":[
                        "finish"
                    ],
                    "type":"string"
                },
                "WithdrawAction":{
                    "title":"WithdrawAction",
                    "type":"object",
                    "properties":{
                        "action":{
                            "$ref":"#/components/schemas/ActionType"
                        }
                    },
                    "required":[
                        "action"
                    ]
                },
                "RebateOut":{
                    "title":"RebateOut",
                    "type":"object",
                    "properties":{
                        "uuid":{
                            "title":"Uuid",
                            "type":"string"
                        },
                        "amount":{
                            "title":"Amount",
                            "type":"number"
                        },
                        "remark":{
                            "title":"Remark",
                            "default":"",
                            "format":"textarea",
                            "type":"string"
                        },
                        "status":{
                            "title":"Status",
                            "type":"string"
                        }
                    },
                    "required":[
                        "uuid",
                        "amount",
                        "status"
                    ]
                },
                "RebateIn":{
                    "title":"RebateIn",
                    "type":"object",
                    "properties":{
                        "agent_uuid":{
                            "title":"Agent Uuid",
                            "type":"string"
                        },
                        "start_date":{
                            "title":"Start Date",
                            "type":"string",
                            "format":"date"
                        },
                        "end_date":{
                            "title":"End Date",
                            "type":"string",
                            "format":"date"
                        },
                        "remark":{
                            "title":"Remark",
                            "default":"",
                            "format":"textarea",
                            "type":"string"
                        }
                    },
                    "required":[
                        "agent_uuid",
                        "start_date",
                        "end_date"
                    ]
                },
                "PagedRebateOut":{
                    "title":"PagedRebateOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/RebateOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                },
                "RebateAction":{
                    "title":"RebateAction",
                    "type":"object",
                    "properties":{
                        "action":{
                            "$ref":"#/components/schemas/ActionType"
                        }
                    },
                    "required":[
                        "action"
                    ]
                },
                "DeveloperNoticeSchema":{
                    "title":"DeveloperNoticeSchema",
                    "type":"object",
                    "properties":{
                        "notice":{
                            "title":"Notice",
                            "format":"md",
                            "type":"string"
                        }
                    },
                    "required":[
                        "notice"
                    ]
                },
                "DeveloperOut":{
                    "title":"DeveloperOut",
                    "type":"object",
                    "properties":{
                        "username":{
                            "title":"Username",
                            "type":"string"
                        },
                        "nickname":{
                            "title":"Nickname",
                            "type":"string"
                        },
                        "mobile":{
                            "title":"Mobile",
                            "type":"string"
                        },
                        "tenant_uuid":{
                            "title":"Tenant Uuid",
                            "type":"string"
                        },
                        "tenant_slug":{
                            "title":"Tenant Slug",
                            "type":"string"
                        },
                        "wallet_total":{
                            "title":"Wallet Total",
                            "type":"number"
                        }
                    },
                    "required":[
                        "username",
                        "nickname",
                        "mobile",
                        "tenant_uuid",
                        "tenant_slug",
                        "wallet_total"
                    ]
                },
                "PagedDeveloperOut":{
                    "title":"PagedDeveloperOut",
                    "type":"object",
                    "properties":{
                        "items":{
                            "title":"Items",
                            "default":[

                            ],
                            "type":"array",
                            "items":{
                                "$ref":"#/components/schemas/DeveloperOut"
                            }
                        },
                        "count":{
                            "title":"Count",
                            "type":"integer"
                        }
                    },
                    "required":[
                        "count"
                    ]
                }
            },
            "securitySchemes":{
                "GlobalAuth":{
                    "type":"http",
                    "scheme":"token"
                }
            }
        },
        "routers":[
            {
                "path":"",
                "name":"\u9996\u9875",
                "icon":"home",
                "page":""
            },
            {
                "path":"developer",
                "name":"\u5f00\u53d1\u5546",
                "icon":"developer",
                "children":[
                    {
                        "path":"app",
                        "name":"\u5e94\u7528\u7ba1\u7406",
                        "icon":"app",
                        "page":""
                    },
                    {
                        "path":"extension",
                        "name":"\u63d2\u4ef6\u7ba1\u7406",
                        "icon":"extend",
                        "page":"extension"
                    },
                    {
                        "path":"notice",
                        "name":"\u5f00\u53d1\u5546\u987b\u77e5",
                        "icon":"notice",
                        "page":""
                    }
                ]
            },
            {
                "path":"agent",
                "name":"\u4ee3\u7406\u5546",
                "icon":"agent",
                "children":[
                    {
                        "path":"info",
                        "name":"\u4ee3\u7406\u8be6\u60c5",
                        "icon":"notice",
                        "page":"agent_info"
                    },
                    {
                        "path":"notice",
                        "name":"\u4ee3\u7406\u5546\u987b\u77e5",
                        "icon":"notice",
                        "page":"agent_notice_readonly"
                    }
                ]
            },
            {
                "path":"cost_center",
                "name":"\u8d39\u7528\u4e2d\u5fc3",
                "icon":"cost",
                "children":[
                    {
                        "path":"orders",
                        "name":"\u8ba2\u5355\u7ba1\u7406",
                        "icon":"order",
                        "children":[
                            {
                                "path":"user",
                                "name":"\u7528\u6237\u8ba2\u5355",
                                "icon":"list",
                                "page":"orders_user"
                            },
                            {
                                "path":"developer",
                                "name":"\u5f00\u53d1\u8005\u8ba2\u5355",
                                "icon":"list",
                                "page":"orders_developer"
                            },
                            {
                                "path":"agent",
                                "name":"\u4ee3\u7406\u5546\u8ba2\u5355",
                                "icon":"list",
                                "page":"orders_agent"
                            }
                        ]
                    },
                    {
                        "path":"withdraw",
                        "name":"\u7ed3\u7b97\u63d0\u73b0",
                        "icon":"list",
                        "page":"withdraw"
                    }
                ]
            },
            {
                "path":"review",
                "name":"\u5ba1\u6838\u7ba1\u7406",
                "icon":"review",
                "children":[
                    {
                        "path":"app",
                        "name":"\u5e94\u7528\u5ba1\u6838",
                        "icon":"app",
                        "page":""
                    },
                    {
                        "path":"extension",
                        "name":"\u63d2\u4ef6\u5ba1\u6838",
                        "icon":"extend",
                        "page":"review"
                    },
                    {
                        "path":"withdraw",
                        "name":"\u63d0\u73b0\u5ba1\u6838",
                        "icon":"list",
                        "page":"withdraw_review"
                    }
                ]
            },
            {
                "path":"developer_manage",
                "name":"\u5f00\u53d1\u5546\u7ba1\u7406",
                "icon":"setting",
                "children":[
                    {
                        "path":"notice",
                        "name":"\u5f00\u53d1\u5546\u987b\u77e5",
                        "icon":"notice",
                        "page":"developer_notice"
                    },
                    {
                        "path":"list",
                        "name":"\u5f00\u53d1\u5546\u5217\u8868",
                        "icon":"list",
                        "page":"developer_list"
                    },
                    {
                        "path":"app_and_extension",
                        "name":"\u5e94\u7528\u4e0e\u63d2\u4ef6\u5217\u8868",
                        "icon":"list",
                        "page":""
                    }
                ]
            },
            {
                "path":"agents",
                "name":"\u4ee3\u7406\u5546\u7ba1\u7406",
                "icon":"setting",
                "children":[
                    {
                        "path":"grade",
                        "name":"\u4ee3\u7406\u5546\u7b49\u7ea7",
                        "icon":"list",
                        "page":"agent_grade"
                    },
                    {
                        "path":"notice",
                        "name":"\u4ee3\u7406\u5546\u987b\u77e5",
                        "icon":"notice",
                        "page":"agent_notice"
                    },
                    {
                        "path":"list",
                        "name":"\u4ee3\u7406\u5546\u5217\u8868",
                        "icon":"list",
                        "page":"agent_manage_list"
                    }
                ]
            },
            {
                "path":"cost_manage",
                "name":"\u8d39\u7528\u7ba1\u7406",
                "icon":"setting",
                "children":[
                    {
                        "path":"order",
                        "name":"\u6240\u6709\u8ba2\u5355",
                        "icon":"list",
                        "page":"orders_list"
                    },
                    {
                        "path":"rebate",
                        "name":"\u4ee3\u7406\u5546\u8fd4\u73b0",
                        "icon":"list",
                        "page":"agent_rebate"
                    },
                    {
                        "path":"income",
                        "name":"\u6536\u5165",
                        "icon":"chart",
                        "page":"income_platform"
                    }
                ]
            }
        ],
        "pages":[
            {
                "name":"extension",
                "description":"\u63d2\u4ef6\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/extensions",
                        "method":"get"
                    },
                    "global":{
                        "create":{
                            "tag":"extension.create",
                            "description":"\u6dfb\u52a0\u63d2\u4ef6"
                        }
                    },
                    "local":{
                        "update":{
                            "tag":"extension.update",
                            "description":"\u7f16\u8f91"
                        },
                        "submit":{
                            "path":"/api/v1/extensions/{extension_uuid}/submit",
                            "method":"get",
                            "description":"\u63d0\u4ea4\u5ba1\u6838"
                        },
                        "delete":{
                            "path":"/api/v1/extensions/{extension_uuid}",
                            "method":"delete",
                            "description":"\u5220\u9664"
                        }
                    }
                }
            },
            {
                "name":"extension.create",
                "description":"\u521b\u5efa\u63d2\u4ef6",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/extensions",
                        "method":"post"
                    },
                    "global":{
                        "create":{
                            "path":"/api/v1/extensions",
                            "method":"post",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"extension.update",
                "description":"\u7f16\u8f91\u63d2\u4ef6",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/extensions/{extension_uuid}",
                        "method":"get"
                    },
                    "global":{
                        "update":{
                            "path":"/api/v1/extensions/{extension_uuid}",
                            "method":"put",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"agent_info",
                "description":"\u4ee3\u7406\u8be6\u60c5",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/agent_info",
                        "method":"get"
                    }
                }
            },
            {
                "name":"review",
                "description":"\u5ba1\u6838\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/extensions?status=submited",
                        "method":"get"
                    },
                    "local":{
                        "check":{
                            "description":"\u5ba1\u6838",
                            "tag":"review.check"
                        }
                    }
                }
            },
            {
                "name":"review.check",
                "description":"\u6dfb\u52a0\u5ba1\u6838\u610f\u89c1",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/extensions/{extension_uuid}/review",
                        "method":"get"
                    },
                    "global":{
                        "approve":{
                            "path":"/api/v1/extensions/{extension_uuid}/reviews/approve",
                            "method":"post",
                            "description":"\u5ba1\u6838\u901a\u8fc7"
                        },
                        "deny":{
                            "path":"/api/v1/extensions/{extension_uuid}/reviews/deny",
                            "method":"post",
                            "description":"\u5ba1\u6838\u62d2\u7edd"
                        }
                    }
                }
            },
            {
                "name":"order",
                "description":"\u8ba2\u5355\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/orders",
                        "method":"get"
                    }
                }
            },
            {
                "name":"wallet",
                "description":"\u8d26\u52a1\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/wallet",
                        "method":"get"
                    }
                }
            },
            {
                "name":"agent_manage_list",
                "description":"\u4ee3\u7406\u5546\u5217\u8868",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/agents",
                        "method":"get"
                    }
                }
            },
            {
                "name":"orders_user",
                "description":"\u7528\u6237\u8ba2\u5355\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/user/orders",
                        "method":"get"
                    }
                }
            },
            {
                "name":"orders_developer",
                "description":"\u5f00\u53d1\u8005\u8ba2\u5355\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/developer/orders",
                        "method":"get"
                    }
                }
            },
            {
                "name":"orders_agent",
                "description":"\u4ee3\u7406\u5546\u8ba2\u5355\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/agent/orders",
                        "method":"get"
                    }
                }
            },
            {
                "name":"withdraw",
                "description":"\u7ed3\u7b97\u63d0\u73b0",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/withdraw",
                        "method":"get"
                    },
                    "global":{
                        "create":{
                            "tag":"withdraw.create",
                            "description":"\u521b\u5efa"
                        }
                    },
                    "local":{
                        "detail":{
                            "tag":"withdraw.detail",
                            "description":"\u8be6\u60c5"
                        },
                        "submit":{
                            "path":"/api/v1/withdraw/{withdraw_uuid}",
                            "method":"post",
                            "description":"\u63d0\u4ea4",
                            "params":{
                                "action":"submit"
                            }
                        }
                    }
                }
            },
            {
                "name":"withdraw.create",
                "description":"\u521b\u5efa\u65b0\u7684\u63d0\u73b0\u8bf7\u6c42",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/withdraw",
                        "method":"post"
                    },
                    "global":{
                        "create":{
                            "path":"/api/v1/withdraw",
                            "method":"post",
                            "description":"\u786e\u8ba4"
                        }
                    }
                }
            },
            {
                "name":"withdraw.detail",
                "description":"\u67e5\u770b\u63d0\u73b0\u8be6\u60c5",
                "page":{
                    "type":"description_page",
                    "init":{
                        "path":"/api/v1/withdraw/{withdraw_uuid}",
                        "method":"get"
                    }
                }
            },
            {
                "name":"orders_list",
                "description":"\u6240\u6709\u8ba2\u5355",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/orders",
                        "method":"get"
                    }
                }
            },
            {
                "name":"income_platform",
                "description":"\u6536\u5165",
                "page":{
                    "type":"description_page",
                    "init":{
                        "path":"/api/v1/income/platform",
                        "method":"get"
                    }
                }
            },
            {
                "name":"agent_notice",
                "description":"\u4ee3\u7406\u5546\u987b\u77e5",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/agent_notice",
                        "method":"get"
                    },
                    "global":{
                        "update":{
                            "tag":"agent_notice.update",
                            "description":"\u7f16\u8f91"
                        }
                    }
                }
            },
            {
                "name":"agent_notice.update",
                "description":"\u7f16\u8f91\u4ee3\u7406\u5546\u987b\u77e5",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/agent_notice",
                        "method":"get"
                    },
                    "global":{
                        "update":{
                            "path":"/api/v1/agent_notice",
                            "method":"post",
                            "description":"\u786e\u8ba4"
                        }
                    }
                }
            },
            {
                "name":"agent_notice_readonly",
                "description":"\u4ee3\u7406\u5546\u987b\u77e5",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/agent_notice",
                        "method":"get"
                    }
                }
            },
            {
                "name":"agent_rebate",
                "description":"\u4ee3\u7406\u5546\u8fd4\u73b0\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/rebate",
                        "method":"get"
                    },
                    "global":{
                        "create":{
                            "tag":"agent_rebate.create",
                            "description":"\u521b\u5efa"
                        }
                    },
                    "local":{
                        "update":{
                            "tag":"agent_rebate.update",
                            "description":"\u7f16\u8f91"
                        },
                        "delete":{
                            "path":"/api/v1/rebate/{rebate_uuid}",
                            "method":"delete",
                            "description":"\u5220\u9664"
                        }
                    }
                }
            },
            {
                "name":"agent_rebate.create",
                "description":"\u521b\u5efa\u4ee3\u7406\u5546\u8fd4\u73b0",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/rebate/{rebate_uuid}",
                        "method":"post"
                    },
                    "global":{
                        "create":{
                            "path":"/api/v1/rebate/{rebate_uuid}",
                            "method":"post",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"agent_rebate.update",
                "description":"\u7f16\u8f91\u4ee3\u7406\u5546\u8fd4\u73b0",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/rebate/{rebate_uuid}",
                        "method":"get"
                    },
                    "global":{
                        "create":{
                            "path":"/api/v1/rebate/{rebate_uuid}",
                            "method":"post",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"agent_grade",
                "description":"\u4ee3\u7406\u5546\u7b49\u7ea7\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/agent_grade",
                        "method":"get"
                    },
                    "global":{
                        "create":{
                            "tag":"agent_grade.create",
                            "description":"\u521b\u5efa"
                        }
                    },
                    "local":{
                        "update":{
                            "tag":"agent_grade.update",
                            "description":"\u7f16\u8f91"
                        },
                        "delete":{
                            "path":"/api/v1/agent_grade/{uuid}",
                            "method":"delete",
                            "description":"\u5220\u9664"
                        }
                    }
                }
            },
            {
                "name":"agent_grade.create",
                "description":"\u521b\u5efa\u65b0\u7684\u4ee3\u7406\u5546\u7b49\u7ea7",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/agent_grade",
                        "method":"post"
                    },
                    "global":{
                        "create":{
                            "path":"/api/v1/agent_grade",
                            "method":"post",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"agent_grade.update",
                "description":"\u7f16\u8f91\u4ee3\u7406\u5546\u7b49\u7ea7",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/agent_grade/{uuid}",
                        "method":"get"
                    },
                    "global":{
                        "create":{
                            "path":"/api/v1/agent_grade/{uuid}",
                            "method":"post",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"withdraw_review",
                "description":"\u63d0\u73b0\u5ba1\u6838\u7ba1\u7406",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/withdraw?action=submit",
                        "method":"get"
                    },
                    "local":{
                        "agree":{
                            "path":"/api/v1/withdraw/{withdraw_uuid}",
                            "method":"post",
                            "description":"\u540c\u610f",
                            "params":{
                                "action":"approve"
                            }
                        },
                        "deny":{
                            "path":"/api/v1/withdraw/{withdraw_uuid}",
                            "method":"post",
                            "description":"\u4e0d\u540c\u610f",
                            "params":{
                                "action":"deny"
                            }
                        }
                    }
                }
            },
            {
                "name":"developer_notice",
                "description":"\u5f00\u53d1\u5546\u987b\u77e5\u7ba1\u7406",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/developer_notice",
                        "method":"get"
                    },
                    "global":{
                        "update":{
                            "tag":"developer_notice.update",
                            "description":"\u7f16\u8f91"
                        }
                    }
                }
            },
            {
                "name":"developer_notice.update",
                "description":"\u7f16\u8f91\u5f00\u53d1\u5546\u987b\u77e5",
                "page":{
                    "type":"form_page",
                    "init":{
                        "path":"/api/v1/developer_notice",
                        "method":"get"
                    },
                    "global":{
                        "update":{
                            "path":"/api/v1/developer_notice",
                            "method":"post",
                            "description":"\u786e\u5b9a"
                        }
                    }
                }
            },
            {
                "name":"developer_list",
                "description":"\u5f00\u53d1\u5546\u5217\u8868",
                "page":{
                    "type":"table_page",
                    "init":{
                        "path":"/api/v1/developers",
                        "method":"get"
                    }
                }
            }
        ],
        "permissions":[
            {
                "name":"normal-user",
                "sort_id":0,
                "type":"group",
                "container":[
                    4
                ]
            },
            {
                "name":"tenant-user",
                "sort_id":1,
                "type":"group",
                "container":[
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    23,
                    29,
                    30,
                    33,
                    34,
                    35,
                    37,
                    38,
                    43,
                    44,
                    45,
                    47,
                    48,
                    49,
                    55
                ]
            },
            {
                "name":"platform-user",
                "sort_id":2,
                "type":"group",
                "container":[
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55
                ]
            },
            {
                "name":"Login",
                "sort_id":3,
                "type":"api",
                "operation_id":"app_auth_login"
            },
            {
                "name":"Callback",
                "sort_id":4,
                "type":"api",
                "operation_id":"app_auth_callback"
            },
            {
                "name":"Upload File",
                "sort_id":5,
                "type":"api",
                "operation_id":"app_file_upload_file"
            },
            {
                "name":"Upload Github",
                "sort_id":6,
                "type":"api",
                "operation_id":"app_file_upload_github"
            },
            {
                "name":"Upload Github Callback",
                "sort_id":7,
                "type":"api",
                "operation_id":"app_file_upload_github_callback"
            },
            {
                "name":"Upload Github Status",
                "sort_id":8,
                "type":"api",
                "operation_id":"app_file_upload_github_status"
            },
            {
                "name":"Download",
                "sort_id":9,
                "type":"api",
                "operation_id":"app_file_download"
            },
            {
                "name":"Create Extension",
                "sort_id":10,
                "type":"api",
                "operation_id":"app_extension_create_extension"
            },
            {
                "name":"Get Extension",
                "sort_id":11,
                "type":"api",
                "operation_id":"app_extension_get_extension"
            },
            {
                "name":"Update Extension",
                "sort_id":12,
                "type":"api",
                "operation_id":"app_extension_update_extension"
            },
            {
                "name":"Delete Extension",
                "sort_id":13,
                "type":"api",
                "operation_id":"app_extension_delete_extension"
            },
            {
                "name":"Create Review",
                "sort_id":14,
                "type":"api",
                "operation_id":"app_extension_create_review"
            },
            {
                "name":"Get On Shelve Extension",
                "sort_id":15,
                "type":"api",
                "operation_id":"app_extension_get_on_shelve_extension"
            },
            {
                "name":"Download Extension",
                "sort_id":16,
                "type":"api",
                "operation_id":"app_extension_download_extension"
            },
            {
                "name":"Create Order",
                "sort_id":17,
                "type":"api",
                "operation_id":"app_order_create_order"
            },
            {
                "name":"User Orders Update",
                "sort_id":18,
                "type":"api",
                "operation_id":"app_order_user_orders_update"
            },
            {
                "name":"User Orders Detail",
                "sort_id":19,
                "type":"api",
                "operation_id":"app_order_user_orders_detail"
            },
            {
                "name":"User Orders Delete",
                "sort_id":20,
                "type":"api",
                "operation_id":"app_order_user_orders_delete"
            },
            {
                "name":"Get Order Detail",
                "sort_id":21,
                "type":"api",
                "operation_id":"app_order_get_order_detail"
            },
            {
                "name":"Delete Order",
                "sort_id":22,
                "type":"api",
                "operation_id":"app_order_delete_order"
            },
            {
                "name":"Pay Notify",
                "sort_id":23,
                "type":"api",
                "operation_id":"app_order_pay_notify"
            },
            {
                "name":"Create Category",
                "sort_id":24,
                "type":"api",
                "operation_id":"app_category_create_category"
            },
            {
                "name":"List Categories",
                "sort_id":25,
                "type":"api",
                "operation_id":"app_category_list_categories"
            },
            {
                "name":"Get Category",
                "sort_id":26,
                "type":"api",
                "operation_id":"app_category_get_category"
            },
            {
                "name":"Update Category",
                "sort_id":27,
                "type":"api",
                "operation_id":"app_category_update_category"
            },
            {
                "name":"Delete Category",
                "sort_id":28,
                "type":"api",
                "operation_id":"app_category_delete_category"
            },
            {
                "name":"Create Review",
                "sort_id":29,
                "type":"api",
                "operation_id":"app_review_create_review"
            },
            {
                "name":"Get Review",
                "sort_id":30,
                "type":"api",
                "operation_id":"app_review_get_review"
            },
            {
                "name":"List Reviews",
                "sort_id":31,
                "type":"api",
                "operation_id":"app_review_list_reviews"
            },
            {
                "name":"Get Extension First Review",
                "sort_id":32,
                "type":"api",
                "operation_id":"app_review_get_extension_first_review"
            },
            {
                "name":"Userinfo",
                "sort_id":33,
                "type":"api",
                "operation_id":"app_user_userinfo"
            },
            {
                "name":"Bind Agent",
                "sort_id":34,
                "type":"api",
                "operation_id":"app_agent_bind_agent"
            },
            {
                "name":"Bind Info",
                "sort_id":35,
                "type":"api",
                "operation_id":"app_agent_bind_info"
            },
            {
                "name":"Create Agent Notice",
                "sort_id":36,
                "type":"api",
                "operation_id":"app_agent_create_agent_notice"
            },
            {
                "name":"Agent Notice Detail",
                "sort_id":37,
                "type":"api",
                "operation_id":"app_agent_agent_notice_detail"
            },
            {
                "name":"Agent Info",
                "sort_id":38,
                "type":"api",
                "operation_id":"app_agent_agent_info"
            },
            {
                "name":"Agent Grade Create",
                "sort_id":39,
                "type":"api",
                "operation_id":"app_agent_agent_grade_create"
            },
            {
                "name":"Agent Grade Update",
                "sort_id":40,
                "type":"api",
                "operation_id":"app_agent_agent_grade_update"
            },
            {
                "name":"Agent Grade Detail",
                "sort_id":41,
                "type":"api",
                "operation_id":"app_agent_agent_grade_detail"
            },
            {
                "name":"Agent Grade Delete",
                "sort_id":42,
                "type":"api",
                "operation_id":"app_agent_agent_grade_delete"
            },
            {
                "name":"Agent Income",
                "sort_id":43,
                "type":"api",
                "operation_id":"app_income_agent_income"
            },
            {
                "name":"Developer Income",
                "sort_id":44,
                "type":"api",
                "operation_id":"app_income_developer_income"
            },
            {
                "name":"Developer Income Detail",
                "sort_id":45,
                "type":"api",
                "operation_id":"app_income_developer_income_detail"
            },
            {
                "name":"Platform Income",
                "sort_id":46,
                "type":"api",
                "operation_id":"app_income_platform_income"
            },
            {
                "name":"Create Withdraw",
                "sort_id":47,
                "type":"api",
                "operation_id":"app_withdraw_create_withdraw"
            },
            {
                "name":"Withdraw Detail",
                "sort_id":48,
                "type":"api",
                "operation_id":"app_withdraw_withdraw_detail"
            },
            {
                "name":"Withdraw Action",
                "sort_id":49,
                "type":"api",
                "operation_id":"app_withdraw_withdraw_action"
            },
            {
                "name":"Create Rebate",
                "sort_id":50,
                "type":"api",
                "operation_id":"app_rebate_create_rebate"
            },
            {
                "name":"Rebate Detail",
                "sort_id":51,
                "type":"api",
                "operation_id":"app_rebate_rebate_detail"
            },
            {
                "name":"Rebate Delete",
                "sort_id":52,
                "type":"api",
                "operation_id":"app_rebate_rebate_delete"
            },
            {
                "name":"Rebate Action",
                "sort_id":53,
                "type":"api",
                "operation_id":"app_rebate_rebate_action"
            },
            {
                "name":"Create Developer Notice",
                "sort_id":54,
                "type":"api",
                "operation_id":"app_developer_create_developer_notice"
            },
            {
                "name":"Developer Notice Detail",
                "sort_id":55,
                "type":"api",
                "operation_id":"app_developer_developer_notice_detail"
            }
        ]
    }
    permission_jsons = response.get('permissions')
    # permission_jsons = {
    #     "permissions":[
    #         {
    #             "name":"normal-user",
    #             "sort_id":0,
    #             "type":"group",
    #             "container":[
    #                 4
    #             ]
    #         },
    #         {
    #             "name":"tenant-user",
    #             "sort_id":1,
    #             "type":"group",
    #             "container":[
    #                 3,
    #                 4,
    #                 5,
    #                 6,
    #                 7,
    #                 8,
    #                 9,
    #                 10,
    #                 11,
    #                 12,
    #                 13,
    #                 14,
    #                 15,
    #                 16,
    #                 17,
    #                 18,
    #                 19,
    #                 20,
    #                 23,
    #                 29,
    #                 30,
    #                 33,
    #                 34,
    #                 35,
    #                 37,
    #                 38,
    #                 43,
    #                 44,
    #                 45,
    #                 47,
    #                 48,
    #                 49,
    #                 55
    #             ]
    #         },
    #         {
    #             "name":"platform-user",
    #             "sort_id":2,
    #             "type":"group",
    #             "container":[
    #                 3,
    #                 4,
    #                 5,
    #                 6,
    #                 7,
    #                 8,
    #                 9,
    #                 10,
    #                 11,
    #                 12,
    #                 13,
    #                 14,
    #                 15,
    #                 16,
    #                 17,
    #                 18,
    #                 19,
    #                 20,
    #                 21,
    #                 22,
    #                 23,
    #                 24,
    #                 25,
    #                 26,
    #                 27,
    #                 28,
    #                 29,
    #                 30,
    #                 31,
    #                 32,
    #                 33,
    #                 35,
    #                 36,
    #                 37,
    #                 38,
    #                 39,
    #                 40,
    #                 41,
    #                 42,
    #                 46,
    #                 47,
    #                 48,
    #                 49,
    #                 50,
    #                 51,
    #                 52,
    #                 53,
    #                 54,
    #                 55
    #             ]
    #         },
    #         {
    #             "name":"Login",
    #             "sort_id":3,
    #             "type":"api",
    #             "operation_id":"app_auth_login"
    #         },
    #         {
    #             "name":"Callback",
    #             "sort_id":4,
    #             "type":"api",
    #             "operation_id":"app_auth_callback"
    #         },
    #         {
    #             "name":"Upload File",
    #             "sort_id":5,
    #             "type":"api",
    #             "operation_id":"app_file_upload_file"
    #         },
    #         {
    #             "name":"Upload Github",
    #             "sort_id":6,
    #             "type":"api",
    #             "operation_id":"app_file_upload_github"
    #         },
    #         {
    #             "name":"Upload Github Callback",
    #             "sort_id":7,
    #             "type":"api",
    #             "operation_id":"app_file_upload_github_callback"
    #         },
    #         {
    #             "name":"Upload Github Status",
    #             "sort_id":8,
    #             "type":"api",
    #             "operation_id":"app_file_upload_github_status"
    #         },
    #         {
    #             "name":"Download",
    #             "sort_id":9,
    #             "type":"api",
    #             "operation_id":"app_file_download"
    #         },
    #         {
    #             "name":"Create Extension",
    #             "sort_id":10,
    #             "type":"api",
    #             "operation_id":"app_extension_create_extension"
    #         },
    #         {
    #             "name":"Get Extension",
    #             "sort_id":11,
    #             "type":"api",
    #             "operation_id":"app_extension_get_extension"
    #         },
    #         {
    #             "name":"Update Extension",
    #             "sort_id":12,
    #             "type":"api",
    #             "operation_id":"app_extension_update_extension"
    #         },
    #         {
    #             "name":"Delete Extension",
    #             "sort_id":13,
    #             "type":"api",
    #             "operation_id":"app_extension_delete_extension"
    #         },
    #         {
    #             "name":"Create Review",
    #             "sort_id":14,
    #             "type":"api",
    #             "operation_id":"app_extension_create_review"
    #         },
    #         {
    #             "name":"Get On Shelve Extension",
    #             "sort_id":15,
    #             "type":"api",
    #             "operation_id":"app_extension_get_on_shelve_extension"
    #         },
    #         {
    #             "name":"Download Extension",
    #             "sort_id":16,
    #             "type":"api",
    #             "operation_id":"app_extension_download_extension"
    #         },
    #         {
    #             "name":"Create Order",
    #             "sort_id":17,
    #             "type":"api",
    #             "operation_id":"app_order_create_order"
    #         },
    #         {
    #             "name":"User Orders Update",
    #             "sort_id":18,
    #             "type":"api",
    #             "operation_id":"app_order_user_orders_update"
    #         },
    #         {
    #             "name":"User Orders Detail",
    #             "sort_id":19,
    #             "type":"api",
    #             "operation_id":"app_order_user_orders_detail"
    #         },
    #         {
    #             "name":"User Orders Delete",
    #             "sort_id":20,
    #             "type":"api",
    #             "operation_id":"app_order_user_orders_delete"
    #         },
    #         {
    #             "name":"Get Order Detail",
    #             "sort_id":21,
    #             "type":"api",
    #             "operation_id":"app_order_get_order_detail"
    #         },
    #         {
    #             "name":"Delete Order",
    #             "sort_id":22,
    #             "type":"api",
    #             "operation_id":"app_order_delete_order"
    #         },
    #         {
    #             "name":"Pay Notify",
    #             "sort_id":23,
    #             "type":"api",
    #             "operation_id":"app_order_pay_notify"
    #         },
    #         {
    #             "name":"Create Category",
    #             "sort_id":24,
    #             "type":"api",
    #             "operation_id":"app_category_create_category"
    #         },
    #         {
    #             "name":"List Categories",
    #             "sort_id":25,
    #             "type":"api",
    #             "operation_id":"app_category_list_categories"
    #         },
    #         {
    #             "name":"Get Category",
    #             "sort_id":26,
    #             "type":"api",
    #             "operation_id":"app_category_get_category"
    #         },
    #         {
    #             "name":"Update Category",
    #             "sort_id":27,
    #             "type":"api",
    #             "operation_id":"app_category_update_category"
    #         },
    #         {
    #             "name":"Delete Category",
    #             "sort_id":28,
    #             "type":"api",
    #             "operation_id":"app_category_delete_category"
    #         },
    #         {
    #             "name":"Create Review",
    #             "sort_id":29,
    #             "type":"api",
    #             "operation_id":"app_review_create_review"
    #         },
    #         {
    #             "name":"Get Review",
    #             "sort_id":30,
    #             "type":"api",
    #             "operation_id":"app_review_get_review"
    #         },
    #         {
    #             "name":"List Reviews",
    #             "sort_id":31,
    #             "type":"api",
    #             "operation_id":"app_review_list_reviews"
    #         },
    #         {
    #             "name":"Get Extension First Review",
    #             "sort_id":32,
    #             "type":"api",
    #             "operation_id":"app_review_get_extension_first_review"
    #         },
    #         {
    #             "name":"Userinfo",
    #             "sort_id":33,
    #             "type":"api",
    #             "operation_id":"app_user_userinfo"
    #         },
    #         {
    #             "name":"Bind Agent",
    #             "sort_id":34,
    #             "type":"api",
    #             "operation_id":"app_agent_bind_agent"
    #         },
    #         {
    #             "name":"Bind Info",
    #             "sort_id":35,
    #             "type":"api",
    #             "operation_id":"app_agent_bind_info"
    #         },
    #         {
    #             "name":"Create Agent Notice",
    #             "sort_id":36,
    #             "type":"api",
    #             "operation_id":"app_agent_create_agent_notice"
    #         },
    #         {
    #             "name":"Agent Notice Detail",
    #             "sort_id":37,
    #             "type":"api",
    #             "operation_id":"app_agent_agent_notice_detail"
    #         },
    #         {
    #             "name":"Agent Info",
    #             "sort_id":38,
    #             "type":"api",
    #             "operation_id":"app_agent_agent_info"
    #         },
    #         {
    #             "name":"Agent Grade Create",
    #             "sort_id":39,
    #             "type":"api",
    #             "operation_id":"app_agent_agent_grade_create"
    #         },
    #         {
    #             "name":"Agent Grade Update",
    #             "sort_id":40,
    #             "type":"api",
    #             "operation_id":"app_agent_agent_grade_update"
    #         },
    #         {
    #             "name":"Agent Grade Detail",
    #             "sort_id":41,
    #             "type":"api",
    #             "operation_id":"app_agent_agent_grade_detail"
    #         },
    #         {
    #             "name":"Agent Grade Delete",
    #             "sort_id":42,
    #             "type":"api",
    #             "operation_id":"app_agent_agent_grade_delete"
    #         },
    #         {
    #             "name":"Agent Income",
    #             "sort_id":43,
    #             "type":"api",
    #             "operation_id":"app_income_agent_income"
    #         },
    #         {
    #             "name":"Developer Income",
    #             "sort_id":44,
    #             "type":"api",
    #             "operation_id":"app_income_developer_income"
    #         },
    #         {
    #             "name":"Developer Income Detail",
    #             "sort_id":45,
    #             "type":"api",
    #             "operation_id":"app_income_developer_income_detail"
    #         },
    #         {
    #             "name":"Platform Income",
    #             "sort_id":46,
    #             "type":"api",
    #             "operation_id":"app_income_platform_income"
    #         },
    #         {
    #             "name":"Create Withdraw",
    #             "sort_id":47,
    #             "type":"api",
    #             "operation_id":"app_withdraw_create_withdraw"
    #         },
    #         {
    #             "name":"Withdraw Detail",
    #             "sort_id":48,
    #             "type":"api",
    #             "operation_id":"app_withdraw_withdraw_detail"
    #         },
    #         {
    #             "name":"Withdraw Action",
    #             "sort_id":49,
    #             "type":"api",
    #             "operation_id":"app_withdraw_withdraw_action"
    #         },
    #         {
    #             "name":"Create Rebate",
    #             "sort_id":50,
    #             "type":"api",
    #             "operation_id":"app_rebate_create_rebate"
    #         },
    #         {
    #             "name":"Rebate Detail",
    #             "sort_id":51,
    #             "type":"api",
    #             "operation_id":"app_rebate_rebate_detail"
    #         },
    #         {
    #             "name":"Rebate Delete",
    #             "sort_id":52,
    #             "type":"api",
    #             "operation_id":"app_rebate_rebate_delete"
    #         },
    #         {
    #             "name":"Rebate Action",
    #             "sort_id":53,
    #             "type":"api",
    #             "operation_id":"app_rebate_rebate_action"
    #         },
    #         {
    #             "name":"Create Developer Notice",
    #             "sort_id":54,
    #             "type":"api",
    #             "operation_id":"app_developer_create_developer_notice"
    #         },
    #         {
    #             "name":"Developer Notice Detail",
    #             "sort_id":55,
    #             "type":"api",
    #             "operation_id":"app_developer_developer_notice_detail"
    #         }
    #     ]
    # }
    # permission_jsons = permission_jsons.get('permissions')
    group_permission_jsons = []
    api_permission_jsons = []
    api_permission_dict = {}
    api_permission_obj_dict = {}
    for permission_json in permission_jsons:
        json_type = permission_json.get('type', '')
        operation_id = permission_json.get('operation_id', '')
        if json_type == 'api':
            api_permission_dict[operation_id] = permission_json
            api_permission_jsons.append(permission_json)
        else:
            group_permission_jsons.append(permission_json)
    # 所有的path
    paths = response.get('paths')
    path_keys = paths.keys()
    # 老的权限(全部重置为没更新)
    base_code = app_temp.name
    base_title = app_temp.name
    tenant = app_temp.tenant
    old_permissions = Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=base_code,
    )
    for old_permission in old_permissions:
        old_permission.is_update = False
        old_permission.save()
    # 开始更新权限path
    for path_key in path_keys:
        item = paths.get(path_key)
        item_keys = item.keys()
        for item_key in item_keys:
            request_obj = item.get(item_key)
            request_type = item_key
            request_url = path_key
            action = request_obj.get('action')
            summary = request_obj.get('summary', '')
            description = request_obj.get('description')
            operation_id = request_obj.get('operationId')
            codename = 'api_{}'.format(uuid.uuid4())
            # 接口权限对象
            api_permission_obj = api_permission_dict.get(operation_id, None)
            sort_id = -1
            container = []
            parent_sort_id = -1
            if api_permission_obj:
                api_permission_name = api_permission_obj.get('name', '')
                if api_permission_name:
                    summary = api_permission_name
                api_permission_sort_id = api_permission_obj.get('sort_id', -1)
                if api_permission_sort_id != -1:
                    sort_id = api_permission_sort_id
                api_permission_parent = api_permission_obj.get('parent', -1)
                if api_permission_parent != -1:
                    parent_sort_id = api_permission_parent
                api_permission_container = api_permission_obj.get('container', [])
                if api_permission_container:
                    container = api_permission_container
            # 权限创建
            permission, is_create = Permission.objects.get_or_create(
                permission_category='API',
                is_system_permission=True,
                app=app_temp,
                is_del=False,
                operation_id=operation_id
            )
            if is_create is True:
                permission.codename = codename
            permission.name = summary
            permission.content_type = None
            permission.tenant = tenant
            permission.is_update = True
            permission.action = action
            permission.base_code = base_code
            permission.description = description
            permission.request_url = request_url
            permission.request_type = request_type
            permission.sort_id = sort_id
            permission.parent_sort_id = parent_sort_id
            permission.container = container
            permission.save()
            api_permission_obj_dict[sort_id] = permission
    # 开始更新权限group
    # for group_permission_json in group_permission_jsons:
    #     group_permission_name = group_permission_json.get('name', '')
    #     group_permission_parent = group_permission_json.get('parent', -1)
    #     group_permission_sort_id = group_permission_json.get('sort_id', -1)
    #     group_permission_container = group_permission_json.get('container', [])
    #     codename = 'group_{}'.format(uuid.uuid4())
    #     # 权限创建
    #     permission, is_create = Permission.objects.get_or_create(
    #         permission_category='GROUP',
    #         is_system_permission=True,
    #         app=app_temp,
    #         is_del=False,
    #         name=group_permission_name
    #     )
    #     if is_create is True:
    #         permission.codename = codename
    #     permission.content_type = None
    #     permission.tenant = tenant
    #     permission.is_update = True
    #     permission.action = ''
    #     permission.base_code = base_code
    #     permission.description = ''
    #     permission.request_url = ''
    #     permission.request_type = ''
    #     permission.parent_sort_id = group_permission_parent
    #     permission.sort_id = group_permission_sort_id
    #     permission.container = group_permission_container
    #     permission.save()
    # 删掉没更新的权限
    Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=base_code,
        is_update=False,
    ).delete()
    # 创建顶级权限分组
    base_permission_group, is_create = PermissionGroup.objects.get_or_create(
        is_active=True,
        is_del=False,
        app=app_temp,
        name=base_title,
        en_name=base_code,
        title=base_title,
        base_code=base_code,
        is_system_group=True,
        is_update=True,
        tenant=tenant,
    )
    # 将权限分组的更新状态全部重置为false
    old_permissiongroups = PermissionGroup.valid_objects.filter(
        title=base_title,
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        base_code=base_code,
        is_update=True,
    ).exclude(uuid=base_permission_group.uuid)
    for old_permissiongroup in old_permissiongroups:
        old_permissiongroup.is_update = False
        old_permissiongroup.save()
    # 处理掉权限分组实体
    for group_permission_json in group_permission_jsons:
        group_permission_name = group_permission_json.get('name', '')
        group_permission_sort_id = group_permission_json.get('sort_id', -1)
        group_permission_parent_sort_id = group_permission_json.get('parent', -1)
        group_permission_container = group_permission_json.get('container', [])
        # parent
        permissiongroup, is_create = PermissionGroup.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name=group_permission_name,
            is_system_group=True,
            base_code=base_code,
            title=base_title,
            app=app_temp,
        )
        if group_permission_parent_sort_id == -1:
            permissiongroup.parent = base_permission_group
        else:
            parent_group_json = find_group_parent(group_permission_jsons, group_permission_parent_sort_id)
            parent_name = parent_group_json.get('name', '')
            parent_sort_id = parent_group_json.get('sort_id', -1)
            parent_container = parent_group_json.get('container', [])
            parent_parent_sort_id = parent_group_json.get('parent', -1)
            # 检查父分组是否存在，如果不存在要创建，开始
            parent_permissiongroup, is_create = PermissionGroup.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name=parent_name,
                is_system_group=True,
                base_code=base_code,
                title=base_title,
                app=app_temp,
            )
            parent_permissiongroup.sort_id = parent_sort_id
            parent_permissiongroup.container = parent_container
            parent_permissiongroup.is_update = True
            parent_permissiongroup.parent_sort_id = parent_parent_sort_id
            parent_permissiongroup.save()
            permissiongroup.parent = parent_permissiongroup
            # 检查父分组是否存在，如果不存在要创建，结束
        permissiongroup.sort_id = group_permission_sort_id
        permissiongroup.container = group_permission_container
        permissiongroup.is_update = True
        permissiongroup.parent_sort_id = group_permission_parent_sort_id
        permissiongroup.save()
        # 扩展分组
        permissiongroup.permissions.clear()
        for group_permission_container_item in group_permission_container:
            permissiongroup.permissions.add(api_permission_obj_dict.get(group_permission_container_item))
    # 删掉没更新的分组数据
    PermissionGroup.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        is_update=False,
        title=base_title,
        base_code=base_code,
    ).exclude(uuid=base_permission_group.uuid).delete()

def find_group_parent(json_objs, sort_id):
    for json_obj in json_objs:
        if json_obj.get('sort_id') == sort_id:
            return json_obj

if __name__ == '__main__':
    client_id = 'NuLbozhXNrMFYpkhKZlfaf724OaoQSSYlACGE5rF'
    # user = User.valid_objects.filter(username='admin').first()
    by_app_client_id_update_permission(client_id)
    # update_user_apppermission(client_id, user.id)