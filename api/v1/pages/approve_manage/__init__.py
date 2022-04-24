from . import approve_action,approve_system
from arkid.core import routers


router = routers.FrontRouter(
    path='approve_manage',
    name='审批管理',
    children=[
        approve_action.router,
        approve_system.router
    ],
)