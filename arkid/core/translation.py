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
    lang_code_list = list(set(list(default_lang_maps.keys())+list(extension_lang_maps.keys())))
    for lang_code in lang_code_list:
        lang_maps[lang_code] = default_lang_maps[lang_code] if lang_code in default_lang_maps.keys() else {}
        
        if lang_code in extension_lang_maps.keys():
            for k in extension_lang_maps[lang_code].keys():
                lang_maps[lang_code].update(extension_lang_maps[lang_code][k])
    return lang_maps

