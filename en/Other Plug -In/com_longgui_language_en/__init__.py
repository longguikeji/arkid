import json
import os
from pathlib import Path
from arkid.core.extension.language import LanguageExtension
from arkid.core.translation import gettext_default as _

class TranslationZhExtension(LanguageExtension):
    def language_type(self) -> str:
        return _("English")
    
    def language_data(self) -> dict:
        rs = {}
        with open(os.path.join(Path(__file__).resolve().parent,'translated.json'),'r') as f:
            data = f.read()
            rs = json.loads(data)
        return rs
    

extension = TranslationZhExtension()

