from typing import Optional

lang_maps = {}

default_lang_maps = {}

default_lang_maps["简体中文"] = {}
default_lang_maps["English"] = {}

def gettext_default(id,msg=None,lang="简体中文"):
    """多语言默认方法

    Args:
        id (str): 标识
        msg (str, optional): 语言文字. Defaults to None.
        lang (str, optional): 语言种类. Defaults to "简体中文".

    Returns:
        str: id 标识
    """
    if not msg:
        msg = id
    
    if lang in default_lang_maps.keys():
        default_lang_maps[lang][id] = msg
    else:
        default_lang_maps[lang] = {
            id:msg
        }

    return id
    

def gettext(id,lang_map: tuple()=("","en"),lang_maps:list(tuple())=None):

    if lang_map:
        msg,lang = lang_map
        gettext_default(id,msg,lang)
    
    if lang_maps:
        for t in lang_maps:
            msg,lang = t
            gettext_default(id,msg,lang)
    
    return id

extension_lang_maps = {}

def reset_lang_maps():
    lang_maps = {}
    from arkid.core.models import LanguageData
    lang_datas = LanguageData.active_objects.all()
    for item in lang_datas:
        if not lang_maps.get(item.name,None):
            lang_maps[item.name] = default_lang_maps[item.name]
        if item.extension_data and isinstance(item.extension_data,dict):
            lang_maps[item.name].update(item.extension_data)
        if item.custom_data and isinstance(item.custom_data,dict):
            lang_maps[item.name].update(item.custom_data)
    return lang_maps

