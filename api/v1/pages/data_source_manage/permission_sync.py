# 权限同步
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

permission_sync_tag = "permission_sync"
permission_sync_name = _("权限数据同步")


page = FormPage(
    name=permission_sync_name,
    tag=permission_sync_tag,
)

register_front_pages(page)

router = router = FrontRouter(
    path=permission_sync_tag,
    name=permission_sync_name,
    page=page,
)