# 图表展示
from arkid.core import routers
from . import bi_systems

router = routers.FrontRouter(
    path='charts',
    name='图表展示',
    children=[
        bi_systems.router
    ]
)