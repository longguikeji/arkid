# 数据源管理
from arkid.core import routers
from . import permission_sync,scim_sync

router = routers.FrontRouter(
    path='data_source',
    name='身份数据源',
    icon='source',
    children=[
        scim_sync.router,
        permission_sync.router,
    ]
)