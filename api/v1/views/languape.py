from typing import List
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from api.v1.schema.languages import LanguageListItemOut, LanguageListOut
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.models import Extension
from arkid.core.translation import default_lang_maps


@api.get("/languages/",response=List[LanguageListItemOut],tags=["语言包管理"],auth=None)
@operation(LanguageListOut)
@paginate(CustomPagination)
def get_app_protocols(request):
    """ 获取语言包列表
    """
    
    return [
        {
            "name": k,
            "count": len(v)
        } for k,v in default_lang_maps.items()
    ]