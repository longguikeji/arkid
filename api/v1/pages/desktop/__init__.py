from . import app_list
from arkid.core import routers,pages

router = routers.FrontRouter(
    path='',
    name='应用',
    icon='home',
    page=app_list.page,
    mobile=True
)

router.hidden = True