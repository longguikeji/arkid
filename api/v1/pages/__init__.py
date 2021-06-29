from . import (
    group, 
    tenant, 
    app, 
    extension,
    maketplace,
    webhook, 
    external_idp, 
    authorization_server,
    authorization_agent,
    user,
    permission,
    profile,
    third_party_account,
    desktop,
    login_config,
    book,
    desktop_config,
    book_config,
    profile_config,
    security,
    tenant_config,
    sub_admin_config,
    agent_rules,
    auth_rules,
    app_permissions,
    permission_group,
    permission_manage,
    scan_code,
    password_factor,
    other_factor,
    data_synchronism,
    custom_process,
    api_document,
    sdk_download,
    log,
    log_config,
    statistics,
    all_tenants,
    all_tenants_config,
    all_users,
    all_users_config
)

from openapi.routers import root_add_routers, Router, PageRouter

root_add_routers([
    PageRouter(
        page=book,
        icon='education'
    ),
    Router(
        path='mine',
        name='个人管理',
        icon='people',
        children=[
            PageRouter(
                page=profile,
                icon='edit'
            ),
            PageRouter(
                page=third_party_account,
                icon='wechat'
            )
        ]
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
                    PageRouter(
                        page=desktop_config,
                        icon='desktop'
                    ),
                    PageRouter(
                        page=book_config,
                        icon='education'
                    ),
                    PageRouter(
                        page=profile_config,
                        icon='people'
                    ),
                    PageRouter(
                        page=security,
                        icon='lock'
                    ),
                    PageRouter(
                        page=sub_admin_config,
                        icon='user'
                    ),
                    PageRouter(
                        page=tenant_config,
                        icon='peoples'
                    )
                ]
            ),
            Router(
                path='app',
                icon='component',
                name='应用管理',
                children=[
                    PageRouter(
                        page=app,
                        icon='list'
                    ),
                    PageRouter(
                        page=agent_rules,
                        icon='example'
                    ),
                    PageRouter(
                        page=auth_rules,
                        icon='lock'
                    ),
                    PageRouter(
                        page=app_permissions,
                        icon='form'
                    )
                ]
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
                    )
                ]
            ),
            Router(
                path='permission',
                name='授权管理',
                icon='list',
                children=[
                    PageRouter(
                        page=permission,
                        icon='list'
                    ),
                    PageRouter(
                        page=permission_group,
                        icon='tree-table'
                    ),
                    PageRouter(
                        page=permission_manage,
                        icon='tree-table'
                    )
                ]
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
                    PageRouter(
                        page=data_synchronism,
                        icon='chart'
                    )
                ]
            ),
            Router(
                path='login_register_config',
                name='登录注册配置',
                icon='lock',
                children=[
                    PageRouter(
                        page=login_config,
                        icon='setting'
                    ),
                    PageRouter(
                        page=external_idp,
                        icon='wechat',
                    ),
                    PageRouter(
                        page=scan_code,
                        icon='scan'
                    )
                ]
            ),
            Router(
                path='authfactor',
                name='认证因素',
                icon='icon',
                children=[
                    PageRouter(
                        page=password_factor,
                        icon='lock'
                    ),
                    PageRouter(
                        page=other_factor,
                        icon='example'
                    )
                ]
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
                    PageRouter(
                        page=custom_process,
                        icon='process'
                    ),
                    PageRouter(
                        page=api_document,
                        icon='connect'
                    ),
                    PageRouter(
                        page=sdk_download,
                        icon='sdk'
                    )
                ]
            ),
            Router(
                path='logmanage',
                name='日志管理',
                icon='edit',
                children=[
                    PageRouter(
                        page=log,
                        icon='list',
                    ),
                    PageRouter(
                        page=log_config,
                        icon='setting',
                    )
                ]    
            ),
            PageRouter(
                page=statistics,
                icon='statistics',
            )
        ]
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
                    PageRouter(
                        page=all_tenants,
                        icon='list'
                    ),
                    PageRouter(
                        page=all_tenants_config,
                        icon='setting'
                    )
                ]
            ),
            Router(
                path='all_users',
                name='用户信息',
                icon='user',
                children=[
                    PageRouter(
                        page=all_users,
                        icon='list'
                    ),
                    PageRouter(
                        page=all_users_config,
                        icon='setting'
                    )
                ]
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
                ]
            )
        ]
    ),
])