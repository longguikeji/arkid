from . import auth_factor,auth_rules,auto_auth,third_auth
from arkid.core import routers

router = routers.FrontRouter(
    path='auth',
    name='认证管理',
    icon='auth',
    children=[
        auth_factor.router,
        third_auth.router,
        auto_auth.router,
        auth_rules.router,
    ],
)