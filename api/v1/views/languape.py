from arkid.core.api import api
from arkid.core.translation import gettext_default as _

@api.get("/languages/",tags=['语言包'])
def get_language_list(request):
    """ 获取语言包列表 TODO
    """
    return []