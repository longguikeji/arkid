#扩展能力  开发者管理
from arkid.core import routers
from . import api_docs,webhook,event_list,chart_test

router = routers.FrontRouter(
    path='developer',
    name='扩展能力',
    icon='developer',
    children=[
        webhook.router,
        event_list.router,
        api_docs.router,
        chart_test.router
    ]
)