from arkid.core.translation import gettext_default as _
from arkid.core import routers

tag = "mine_auth_manage"
name = _("认证管理")

router = routers.FrontRouter(
    path=tag,
    name=name,
)