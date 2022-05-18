# 图表展示
from arkid.core import routers
from . import bi_systems,charts

router = routers.FrontRouter(
    path='charts',
    name='图表分析',
    children=[
        charts.router,
        bi_systems.router,
    ]
)