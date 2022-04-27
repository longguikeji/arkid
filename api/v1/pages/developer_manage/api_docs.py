# BI系统
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _

api_docs_tag = "api_docs"
api_docs_name = _("API文档")

router = FrontRouter(
    path=api_docs_tag,
    name=api_docs_name,
    url='/api/v1/redoc'
)