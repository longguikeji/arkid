from arkid.spectacular_settings import SPECTACULAR_SETTINGS

def root_add_roles_describe(roles_describe:list):
    SPECTACULAR_SETTINGS['EXTENSIONS_INFO']['roles_describe'] = roles_describe