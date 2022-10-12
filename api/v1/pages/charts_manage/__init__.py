# 图表展示
from arkid.core import routers
from . import bi_systems,charts

router = routers.FrontRouter(
    path='charts_manage',
    name='图表分析',
    icon='charts_manage',
    children=[
        charts.router,
        bi_systems.router,
    ]
)