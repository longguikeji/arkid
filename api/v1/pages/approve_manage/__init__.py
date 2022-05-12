from . import approve_action, approve_system, all_approve_requests
from arkid.core import routers


router = routers.FrontRouter(
    path='approve_manage',
    name='审批管理',
    children=[
        approve_action.router,
        all_approve_requests.router,
        approve_system.router,
    ],
)
