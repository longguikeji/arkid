from . import user_list
from arkid.core import routers


router = routers.FrontRouter(
    path='user',
    name='用户管理',
    icon='user',
    children=[
        user_list.router,
    ],
)

# router.change_page_tag('core')