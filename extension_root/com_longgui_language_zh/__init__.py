from arkid.core.extension.language import LanguageExtension
from arkid.core.translation import gettext_default as _

class TranslationZhExtension(LanguageExtension):
    def language_type(self) -> str:
        return _("简体中文")
    
    def language_data(self) -> dict:
        return {
            "data":"数据"
        }
    

extension = TranslationZhExtension()

