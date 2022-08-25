from . import mine_app_group_list
from arkid.core import routers,pages

router = routers.FrontRouter(
    path='',
    name='应用',
    icon='home',
    page=mine_app_group_list.page,
    mobile=True
)

router.hidden = True