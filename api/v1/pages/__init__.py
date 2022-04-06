from . import user
from arkid.core import routers


routers.register_front_routers(
    [
        user.router,
    ]
)
