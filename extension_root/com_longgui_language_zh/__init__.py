import uuid
import json
import logging
from .constants import KEY
from arkid import core
from arkid.core import extension, event
from arkid.core.extension.language import LanguageExtension
from arkid.core.translation import gettext_default as _
from django.conf import settings
import os

    
class TranslationZhExtension(LanguageExtension):
    def language_type(self) -> str:
        return _("简体中文")
    
    def language_data(self) -> dict:
        return {
            "data":"数据"
        }
    

extension = TranslationZhExtension()

