#扩展能力  开发者管理
from arkid.core import routers
from . import api_docs,webhook,event_list

router = routers.FrontRouter(
    path='developer',
    name='扩展能力',
    children=[
        webhook.router,
        event_list.router,
        api_docs.router,
    ]
)