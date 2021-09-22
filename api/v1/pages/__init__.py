from . import (
    admin_log,
    all_tenants,
    all_tenants_config,
    all_users,
    all_users_config,
    app,
    authorization_server,
    authorization_agent,
    auth_rules,
    contacts,
    contacts_switch,
    contacts_group_config,
    contacts_user_config,
    desktop,
    custom_process,
    data_synchronism,
    desktop_config,
    device,
    extension,
    external_idp,
    group,
    login_register_config,
    log_config,
    maketplace,
    other_auth_factor,
    # password_factor,
    permission,
    profile,
    profile_config,
    permission_group,
    permission_manage,
    sdk_download,
    system_config,
    system_password,
    statistics,
    subuser,
    sub_admin_config,
    tenant,
    tenant_config,
    third_part_account,
    user,
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
            name='租户管理',
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
                                Router(
                                    path='contacts_config',
                                    name='通讯录设置',
                                    icon='education',
                                    children=[
                                        PageRouter(
                                            page=contacts_switch, icon='setting'
                                        ),
                                        PageRouter(
                                            page=contacts_group_config, icon='peoples'
                                        ),
                                        PageRouter(
                                            page=contacts_user_config, icon='people'
                                        ),
                                    ],
                                ),
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
                    icon='list',
                    children=[
                        PageRouter(page=permission, icon='list'),
                        PageRouter(page=permission_group, icon='tree-table'),
                        PageRouter(page=permission_manage, icon='tree-table'),
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
                        PageRouter(
                            page=external_idp,
                            icon='wechat',
                        ),
                        # PageRouter(page=password_factor, icon='lock'),
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
            name='系统管理',
            icon='setting',
            children=[
                Router(
                    path='all_tenants',
                    name='租户信息',
                    icon='peoples',
                    children=[
                        PageRouter(page=all_tenants, icon='list'),
                        PageRouter(page=all_tenants_config, icon='setting'),
                    ],
                ),
                Router(
                    path='all_users',
                    name='用户信息',
                    icon='user',
                    children=[
                        PageRouter(page=all_users, icon='list'),
                        PageRouter(page=all_users_config, icon='setting'),
                    ],
                ),
                Router(
                    path='system_config',
                    name='系统配置',
                    icon='setting',
                    children=[
                        PageRouter(page=system_config, icon='setting'),
                        # PageRouter(page=system_password, icon='lock'),
                    ],
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