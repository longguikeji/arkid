from . import user,desktop
from arkid.core import routers


routers.register_front_routers(
    [
        desktop.router,
        user.router,
    ]
)
