from . import user,desktop,app
from arkid.core import routers


routers.register_front_routers(
    [
        desktop.router,
        user.router,
        app.router
    ]
)
