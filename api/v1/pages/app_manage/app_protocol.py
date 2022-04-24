# 应用协议
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

app_protocol_tag = "app_protocol"
app_protocol_name = _("应用协议")


page = FormPage(
    name=app_protocol_name,
    tag=app_protocol_tag,
)

register_front_pages(page)

router = FrontRouter(
    path=app_protocol_tag,
    name=app_protocol_name,
    icon='app',
    page=page,
)