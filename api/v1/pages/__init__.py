from . import (
    admin_log,
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
    maketplace,
    other_auth_factor,
    permission,
    profile,
    profile_config,
    permission_group,
    sdk_download,
    system_config,
    system_password,
    statistics,
    subuser,
    sub_admin_config,
    tenant,
    tenant_config,
    tenant_switch,
    third_part_account,
    user,
    user_permission,
    user_log,
    user_login_log,
    webhook,
)

from openapi.routers import root_add_routers, Router, PageRouter, UrlRouter

root_add_routers(
    [
        PageRouter(page=desktop, icon='desktop'),
        PageRouter(page=contacts, icon='education'),
        Router(
            path='mine',
            name='个人管理',
            icon='people',
            children=[
                PageRouter(page=profile, icon='edit'),
                PageRouter(page=third_part_account, icon='wechat'),
                PageRouter(page=subuser, icon='user'),
                PageRouter(page=user_login_log, icon='lock'),
            ],
        ),
        Router(
            path='tmanage',
            name='系统管理',
            icon='peoples',
            children=[
                Router(
                    path='tconfig',
                    name='租户设置',
                    icon='setting',
                    children=[
                        PageRouter(page=tenant_config, icon='peoples'),
                        Router(
                            path='umanage',
                            name='用户管理配置',
                            icon='people',
                            children=[
                                PageRouter(page=desktop_config, icon='desktop'),
                                PageRouter(page=contacts_config, icon='education'),
                                PageRouter(page=profile_config, icon='setting'),
                            ],
                        ),
                        PageRouter(page=sub_admin_config, icon='user'),
                    ],
                ),
                Router(
                    path='app',
                    icon='component',
                    name='应用管理',
                    children=[
                        PageRouter(page=app, icon='list'),
                        PageRouter(page=auth_rules, icon='lock'),
                    ],
                ),
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
                        PageRouter(page=device, icon='developer'),
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
                                PageRouter(page=app_permission, icon='list')
                            ]
                        ),
                    ],
                ),
                Router(
                    path='source',
                    name='连接身份源',
                    icon='component',
                    children=[
                        PageRouter(
                            page=authorization_server,
                            icon='list',
                        ),
                        PageRouter(
                            page=authorization_agent,
                            icon='list',
                        ),
                        PageRouter(page=data_synchronism, icon='chart'),
                    ],
                ),
                Router(
                    path='authfactor',
                    name='认证因素',
                    icon='lock',
                    children=[
                        PageRouter(page=login_register_config, icon='setting'),
                        PageRouter(page=external_idp,icon='wechat'),
                        PageRouter(page=other_auth_factor, icon='example'),
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
                        PageRouter(page=custom_process, icon='process'),
                        UrlRouter(
                            path='document',
                            name='API文档',
                            url='/api/schema/redoc/',
                            icon='connect',
                        ),
                        PageRouter(page=sdk_download, icon='sdk'),
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
            ],
        ),
        Router(
            path='system',
            name='平台管理',
            icon='setting',
            children=[
                PageRouter(
                    page=tenant_switch,
                    icon='setting',
                ),
                Router(
                    path='extension',
                    name='插件管理',
                    icon='list',
                    children=[
                        PageRouter(
                            page=extension,
                            icon='list',
                        ),
                        PageRouter(
                            page=maketplace,
                            icon='list',
                        ),
                    ],
                ),
            ],
        ),
    ]
)
