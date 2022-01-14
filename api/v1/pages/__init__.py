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
    notice,
    notice_manage,
    announcement,
    message,
    knowledge_base,
    ticket,
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
    application_account,
    multiple_ips,
    application_account_settings,
    application_group,
    application_settings,
    data_sync,
    backend_login,
)

from openapi.routers import root_add_routers, Router, PageRouter, UrlRouter

root_add_routers(
    [
        PageRouter(page=desktop, icon='desktop'),
        PageRouter(page=contacts, icon='contacts'),
        PageRouter(page=mine, icon='user'),
        PageRouter(page=notice, icon='notice'),
        Router(
            path='message_center',
            name='消息中心',
            icon='message',
            children=[
                PageRouter(page=notice_manage, icon='list'),
                PageRouter(page=knowledge_base, icon='list'),
                PageRouter(page=ticket, icon='list'),
                PageRouter(page=announcement, icon='list'),
                PageRouter(page=message, icon='list'),
            ]
        ),
        Router(
            path='app_manage',
            name='应用管理',
            icon='app',
            children=[
                PageRouter(
                    page=app,
                    icon='app',
                ),
                PageRouter(
                    page=multiple_ips,
                    icon='list',
                ),
                PageRouter(
                    page=application_group,
                    icon='list',
                ),
                PageRouter(
                    page=application_settings,
                    icon='list',
                ),
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
                    icon='list',
                ),
                PageRouter(page=all_tenant, icon='list'),
                PageRouter(page=device, icon='device'),
                PageRouter(page=application_account, icon='list'),
            ],
        ),
        Router(
            path='permission',
            name='授权管理',
            icon='auth',
            children=[
                PageRouter(page=permission, icon='list'),
                PageRouter(page=permission_group, icon='list'),
                Router(
                    path='permission_manage',
                    name='权限管理',
                    icon='setting',
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
            icon='source',
            children=[
                PageRouter(
                    page=authorization_server,
                    icon='list',
                ),
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
                PageRouter(page=backend_login,icon='setting'),
                PageRouter(page=other_auth_factor, icon='auth'),
                PageRouter(page=auth_rules, icon='lock')
            ],
        ),
        Router(
            path='developer',
            name='扩展能力',
            icon='extend',
            children=[
                PageRouter(
                    page=webhook,
                    icon='hook',
                ),
                UrlRouter(
                    path='document',
                    name='API文档',
                    url='/api/schema/redoc/',
                    icon='api',
                ),
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
            icon='bar',
        ),
        Router(
            path='tconfig',
            name='租户设置',
            icon='setting',
            children=[
                PageRouter(page=tenant_config, icon='tenant'),
                PageRouter(page=sub_admin_config, icon='user')
            ]
        ),
        Router(
            path='umanage',
            name='用户设置',
            icon='user',
            children=[
                PageRouter(page=desktop_config, icon='desktop'),
                PageRouter(page=contacts_config, icon='contacts'),
                PageRouter(page=profile_config, icon='setting'),
            ]
        ),
        Router(
            path='system',
            name='平台管理',
            icon='setting',
            children=[
                PageRouter(
                    page=extension,
                    icon='list'
                ),
                PageRouter(
                    page=tenant_switch,
                    icon='setting',
                )
            ],
        ),
    ]
)
