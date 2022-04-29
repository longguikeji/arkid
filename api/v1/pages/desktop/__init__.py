from . import app_list
from .. import mine
from arkid.core import routers,pages

router = routers.FrontRouter(
    path='',
    name='桌面',
    icon='home',
    page=app_list.page
)

router.mobile_children = [
    # mine.auth_manage.router,
    mine.router,
]

router.hidden = True