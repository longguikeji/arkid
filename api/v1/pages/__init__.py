from . import (
    admin_log,
    all_tenant,
    app,
    app_permission,
    authorization_server,
    authorization_agent,
    auth_rules,
    contacts,
    contacts_config,
    desktop,
    custom_process,
    data_synchronism,
    desktop_config,
    device,
    extension,
    external_idp,
    group,
    group_permission,
    login_register_config,
    log_config,
    mine,
    other_auth_factor,
    permission,
    profile_config,
    permission_group,
    sdk_download,
    statistics,
    sub_admin_config,
    tenant,
    tenant_config,
    tenant_switch,
    user,
    user_permission,
    user_log,
    webhook,
    data_sync,
    backend_login,
    app_account,
    bind_saas,
    arkstore,
)

from openapi.routers import root_add_routers, Router, PageRouter, UrlRouter
from openapi.describe import root_add_roles_describe

root_add_routers(
    [
        PageRouter(page=desktop, icon='desktop'),
        PageRouter(page=contacts, icon='education'),
        PageRouter(page=mine, icon='people'),
        PageRouter(page=app, icon='component'),
        Router(
            path='user',
            name='用户管理',
            icon='user',
            children=[
                PageRouter(
                    page=user,
                    icon='list',
                ),
                PageRouter(
                    page=group,
                    icon='tree-table',
                ),
                PageRouter(page=all_tenant, icon='list'),
                PageRouter(page=device, icon='developer'),
                PageRouter(page=app_account, icon='list'),
            ],
        ),
        Router(
            path='permission',
            name='授权管理',
            icon='tree-table',
            children=[
                PageRouter(page=permission, icon='list'),
                PageRouter(page=permission_group, icon='list'),
                Router(
                    path='permission_manage',
                    name='权限管理',
                    icon='tree-table',
                    children=[
                        PageRouter(page=user_permission, icon='list'),
                        PageRouter(page=group_permission, icon='list'),
                        PageRouter(page=app_permission, icon='list'),
                    ],
                ),
            ],
        ),
        Router(
            path='source',
            name='连接身份源',
            icon='source',
            children=[
                PageRouter(
                    page=authorization_server,
                    icon='list',
                ),
                # PageRouter(
                #     page=authorization_agent,
                #     icon='list',
                # ),
                PageRouter(page=data_sync, icon='chart'),
            ],
        ),
        Router(
            path='authfactor',
            name='认证因素',
            icon='lock',
            children=[
                PageRouter(page=login_register_config, icon='setting'),
                PageRouter(page=external_idp, icon='wechat'),
                PageRouter(page=backend_login, icon='setting'),
                PageRouter(page=other_auth_factor, icon='example'),
                PageRouter(page=auth_rules, icon='lock'),
            ],
        ),
        Router(
            path='developer',
            name='扩展能力',
            icon='developer',
            children=[
                PageRouter(
                    page=webhook,
                    icon='webhook',
                ),
                # PageRouter(page=custom_process, icon='process'),
                UrlRouter(
                    path='document',
                    name='API文档',
                    url='/api/schema/redoc/',
                    icon='connect',
                ),
                # PageRouter(page=sdk_download, icon='sdk'),
            ],
        ),
        Router(
            path='logmanage',
            name='日志管理',
            icon='edit',
            children=[
                PageRouter(
                    page=user_log,
                    icon='list',
                ),
                PageRouter(
                    page=admin_log,
                    icon='list',
                ),
                PageRouter(
                    page=log_config,
                    icon='setting',
                ),
            ],
        ),
        PageRouter(
            page=statistics,
            icon='statistics',
        ),
        Router(
            path='tconfig',
            name='租户设置',
            icon='setting',
            children=[
                PageRouter(page=tenant_config, icon='peoples'),
                PageRouter(page=sub_admin_config, icon='user'),
            ],
        ),
        Router(
            path='umanage',
            name='用户设置',
            icon='people',
            children=[
                PageRouter(page=desktop_config, icon='desktop'),
                PageRouter(page=contacts_config, icon='education'),
                PageRouter(page=profile_config, icon='setting'),
            ],
        ),
        Router(
            path='extension',
            name='插件管理',
            icon='setting',
            children=[
                PageRouter(page=bind_saas, icon='list'),
                PageRouter(page=arkstore, icon='setting'),
            ],
        ),
        Router(
            path='system',
            name='平台管理',
            icon='setting',
            children=[
                PageRouter(page=extension, icon='list'),
                PageRouter(
                    page=tenant_switch,
                    icon='setting',
                ),
            ],
        ),
    ]
)

root_add_roles_describe({
    'code':'arkid',
    'name': 'ArkID',
    'children':[
        {
            'code':'globaladmin',
            'name':'超级管理员'
        },
        {
            'code':'tenantadmin',
            'name':'租户管理员'
        },
        {
            'code':'generaluser',
            'name':'普通用户'
        },
        {
            'code':'appmanage',
            'name':'应用管理'
        },
        {
            'code':'usermanage',
            'name':'用户管理',
            'children': [
                {
                    'code': 'userlist',
                    'name': '用户列表'
                },
                {
                    'code': 'groupmanage',
                    'name': '分组管理'
                },
                {
                    'code': 'tenantlist',
                    'name': '租户列表'
                },
                {
                    'code': 'devicemanage',
                    'name': '设备管理'
                },
                {
                    'code': 'fillformaccount',
                    'name': '表单代填账号'
                }
            ]
        },
        {
            'code':'authmanage',
            'name':'授权管理',
            'children': [
                {
                    'code': 'permissionlist',
                    'name': '权限列表'
                },
                {
                    'code': 'permissiongroup',
                    'name': '权限分组'
                },
                {
                    'code': 'permissionmanage',
                    'name': '权限管理'
                }
            ]
        },
        {
            'code':'linkidentity',
            'name':'连接身份源',
            'children': [
                {
                    'code': 'identityservice',
                    'name': '身份源服务'
                },
                {
                    'code': 'datasync',
                    'name': '数据同步'
                }
            ]
        },
        {
            'code':'authfactor',
            'name':'认证因素',
            'children': [
                {
                    'code': 'factorconfig',
                    'name': '因素配置'
                },
                {
                    'code': 'thirdpartylogin',
                    'name': '第三方登录'
                },
                {
                    'code': 'backendauth',
                    'name': '后端认证'
                },
                {
                    'code': 'otherauthfactor',
                    'name': '其它认证因素'
                }
            ]
        },
        {
            'code':'expansionable',
            'name':'扩展能力',
            'children': [
                {
                    'code': 'webhook',
                    'name': 'Webhook'
                },
                {
                    'code': 'apidocument',
                    'name': 'API文档'
                }
            ]
        },
        {
            'code':'logmanage',
            'name':'日志管理',
            'children': [
                {
                    'code': 'useractionlog',
                    'name': '用户行为日志'
                },
                {
                    'code': 'manageractionlog',
                    'name': '管理员行为日志'
                },
                {
                    'code': 'logset',
                    'name': '日志设置'
                }
            ]
        },
        {
            'code':'statisticalgraph',
            'name':'统计图表'
        },
        {
            'code':'tenantset',
            'name':'租户设置',
            'children': [
                {
                    'code': 'tenantconfig',
                    'name': '租户配置'
                },
                {
                    'code': 'childmanagerset',
                    'name': '子管理员设置'
                }
            ]
        },
        {
            'code':'userset',
            'name':'用户设置',
            'children': [
                {
                    'code': 'desktopset',
                    'name': '桌面设置'
                },
                {
                    'code': 'contactsset',
                    'name': '通讯录设置'
                },
                {
                    'code': 'profileset',
                    'name': '个人资料设置'
                }
            ]
        },
        {
            'code':'userset',
            'name':'用户设置',
            'children': [
                {
                    'code': 'desktopset',
                    'name': '桌面设置'
                },
                {
                    'code': 'contactsset',
                    'name': '通讯录设置'
                },
                {
                    'code': 'profileset',
                    'name': '个人资料设置'
                }
            ]
        },
        {
            'code':'platformmanage',
            'name':'平台管理',
            'children': [
                {
                    'code': 'pluginconfig',
                    'name': '插件配置'
                },
                {
                    'code': 'platformconfig',
                    'name': '平台配置'
                }
            ]
        }
    ]
})

# root_add_roles_describe({
#     # 基础角色
#     'globaladmin': '超级管理员',
#     'tenantadmin': '租户管理员',
#     'generaluser': '普通用户',
#     # 菜单
#     'appmanage': '应用管理',

#     'usermanage': '用户管理',
#     'usermanage.userlist': '用户列表',
#     'usermanage.groupmanage': '分组管理',
#     'usermanage.tenantlist': '租户列表',
#     'usermanage.devicemanage': '设备管理',
#     'usermanage.fillformaccount': '表单代填账号',

#     'authmanage': '授权管理',
#     'authmanage.permissionlist': '权限列表',
#     'authmanage.permissiongroup': '权限分组',
#     'authmanage.permissionmanage': '权限管理',

#     'linkidentity': '连接身份源',
#     'linkidentity.identityservice': '身份源服务',
#     'linkidentity.datasync': '数据同步',

#     'authfactor': '认证因素',
#     'authfactor.factorconfig': '因素配置',
#     'authfactor.thirdpartylogin': '第三方登录',
#     'authfactor.backendauth': '后端认证',
#     'authfactor.otherauthfactor': '其它认证因素',

#     'expansionable': '扩展能力',
#     'expansionable.webhook': 'Webhook',
#     'expansionable.apidocument': 'API文档',

#     'logmanage': '日志管理',
#     'logmanage.useractionlog': '用户行为日志',
#     'logmanage.manageractionlog': '管理员行为日志',
#     'logmanage.logset': '日志设置',

#     'statisticalgraph': '统计图表',

#     'tenantset': '租户设置',
#     'tenantset.tenantconfig': '租户配置',
#     'tenantset.childmanagerset': '子管理员设置',

#     'userset': '用户设置',
#     'userset.desktopset': '桌面设置',
#     'userset.contactsset': '通讯录设置',
#     'userset.profileset': '个人资料设置',

#     'platformmanage': '平台管理',
#     'platformmanage.pluginconfig': '插件配置',
#     'platformmanage.platformconfig': '平台配置'
# })
