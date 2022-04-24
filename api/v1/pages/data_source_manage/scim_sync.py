# 用户/用户分组数据同步 基于SCIM协议
from arkid.core.routers import FrontRouter
from arkid.core.translation import gettext_default as _
from arkid.core.pages import FormPage,register_front_pages

scim_sync_tag = "scim_sync"
scim_sync_name = _("用户数据同步(基于SCIM协议)")


page = FormPage(
    name=scim_sync_name,
    tag=scim_sync_tag,
)

register_front_pages(page)

router = router = FrontRouter(
    path=scim_sync_tag,
    name=scim_sync_name,
    page=page,
)