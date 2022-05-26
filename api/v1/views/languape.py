from typing import List

from django.shortcuts import get_object_or_404
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from api.v1.schema.languages import *
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.models import LanguageData
from arkid.core.translation import lang_maps,reset_lang_maps
from arkid.core.error import ErrorCode


@api.get("/tenant/{tenant_id}/languages/",response=List[LanguageListItemOut],tags=["语言包管理"],auth=None)
@operation(LanguageListOut)
@paginate(CustomPagination)
def get_languages(request,tenant_id:str):
    """ 获取语言包列表
    """
    language_datas = LanguageData.active_objects.all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "count": item.count,
            "extension_name": item.extension.name if item.extension else "",
            "extension_package": item.extension.package if item.extension else ""
        } for item in language_datas
    ]
    
@api.post(
    "/tenant/{tenant_id}/languages/",
    tags=["语言包管理"],
    auth=None,
    response=LanguageCreateOut,
)
def create_language(request, tenant_id: str,data:LanguageCreateIn):
    """ 创建自定义语言包
    """
    language_data = LanguageData.objects.create(
        **data.dict()
    )
    
    return {'error': ErrorCode.OK.value}

@api.delete(
    "/tenant/{tenant_id}/languages/{id}/",
    tags=["语言包管理"],
    auth=None,
    response=LanguageDeleteOut,
)
def delete_language(request, tenant_id: str,id:str):
    """ 创建自定义语言包
    """
    language_data = get_object_or_404(
        LanguageData.active_objects,
        id=id
    )
    if language_data.extension:
        # 如果是插件中创建的语言包，仅删除自定义的词句
        language_data.custom_data=None
        language_data.save()
    else:
        language_data.delete()
    return {'error': ErrorCode.OK.value}

@api.get(
    "/tenant/{tenant_id}/languages/{id}/translates/",
    tags=["语言包管理"],
    auth=None,
    response=List[LanguageDataItemOut],
)
@operation(LanguageDataOut)
@paginate(CustomPagination)
def get_language_data(request, tenant_id: str,id:str):
    """ 获取自定义语言包
    """
    language_data = get_object_or_404(
        LanguageData.active_objects,
        id=id
    )
    
    return [{"source":k,"translated":v} for k,v in language_data.data.items()]

@api.post(
    "/tenant/{tenant_id}/languages/{id}/translates/",
    tags=["语言包管理"],
    auth=None,
    response=LanguageDataItemCreateOut,
)
@operation(LanguageDataItemCreateOut)
def create_language_data(request, tenant_id: str, id:str, data:LanguageDataItemCreateIn):
    """ 创建自定义语言包翻译
    """
    language_data = get_object_or_404(
        LanguageData.active_objects,
        id=id
    )
    
    custom_translate_data = {data.source:data.translated}
    if language_data.custom_data:
        language_data.custom_data.update(custom_translate_data)
    else:
        language_data.custom_data = custom_translate_data
    language_data.save()
    lang_maps = reset_lang_maps()
    return {'error': ErrorCode.OK.value}

@api.get(
    "/tenant/{tenant_id}/translate_word/",
    tags=["语言包管理"],
    auth=None,
    response=LanguageTranslateWordOut,
)
@operation(LanguageTranslateWordOut)
def get_language_data(request, tenant_id: str):
    """ 获取自定义语言包
    """
    return lang_maps.keys()