#扩展能力  开发者管理
from arkid.core import routers
from . import api_docs,webhook

router = routers.FrontRouter(
    path='developer',
    name='扩展能力',
    children=[
        api_docs.router,
        webhook.router
    ]
)