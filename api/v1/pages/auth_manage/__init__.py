from . import auth_factor,auth_rules,auto_auth,third_auth
from arkid.core import routers

router = routers.FrontRouter(
    path='auth',
    name='认证管理',
    children=[
        auth_factor.router,
        auth_rules.router,
        auto_auth.router,
        third_auth.router
    ],
)