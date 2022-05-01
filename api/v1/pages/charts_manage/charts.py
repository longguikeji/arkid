from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'charts'
name = '图表分析'


page = pages.DescriptionPage(tag=tag, name=name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)