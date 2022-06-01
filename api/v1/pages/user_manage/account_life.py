from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'account_life'
name = '账号生命周期'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑账号生命周期设置"))
edit_cron_page = pages.FormPage(name=_("编辑账号生命周期定时任务"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(edit_cron_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='life',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/account_lifes/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/account_lifes/',
        ),
        'edit_crontab': actions.OpenAction(
            page=edit_cron_page, name=_('Edit Account Life Crontab', '编辑生命周期定时任务')
        ),
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete": actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/account_lifes/{id}/",
        ),
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/account_lifes/{id}/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/account_lifes/{id}/"
        ),
    },
)

edit_cron_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/account_life_crontab/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/account_life_crontab/",
            method=actions.FrontActionMethod.PUT,
        ),
    },
)
