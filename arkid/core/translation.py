from typing import Optional


lang_maps = {}

default_lang_maps = {}


def gettext_default(id,msg="",lang="en"):
    if not msg:
        if lang=='en':
            msg = id
        else:
            raise Exception("invalid params")
    
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

