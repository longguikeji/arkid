# BI系统
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _

tag = "api_docs"
name = _("API文档")

router = FrontRouter(
    path=tag,
    name=name,
    url='/api/v1/tenant/{tenant_}docs/redoc/'
)