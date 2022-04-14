from arkid.core import routers, pages

user_list_tag = 'user_list'
user_list_name = '用户列表'


router = routers.FrontRouter(
    path=user_list_tag,
    name='用户管理',
    icon='user',
    page=user_list_tag,
)


page = pages.FrontPage(
    tag = user_list_tag, 
    name = user_list_name,
    type = pages.TABLE_PAGE_TYPE,
    init_action=pages.FrontAction(
        path = '/api/v1/tenant/{parent_lookup_tenant}/user/',
        method = 'get'
    )
)

pages.register_front_pages(page)
