# BI系统
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

bi_systems_tag = "bi_systems"
bi_systems_name = _("BI系统")


page = FormPage(
    name=bi_systems_name,
    tag=bi_systems_tag,
)

register_front_pages(page)

router = router = FrontRouter(
    path=bi_systems_tag,
    name=bi_systems_name,
    page=page,
)