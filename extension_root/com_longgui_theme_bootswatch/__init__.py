from arkid.core.extension.front_theme import FrontThemeExtension, BaseFrontThemeConfigSchema
from pydantic import Field
from typing import List, Optional, Literal
from arkid.core.translation import gettext_default as _
from arkid.core.extension import create_extension_schema_by_package


class ThemeBootswatch(FrontThemeExtension):
    def load(self):
        self.register_front_theme('materia', 'https://bootswatch.com/5/materia/bootstrap.min.css')
        self.register_front_theme('darkly', 'https://bootswatch.com/5/darkly/bootstrap.min.css')
        self.register_front_theme('yeti', 'https://bootswatch.com/5/yeti/bootstrap.min.css')
        return super().load()


extension = ThemeBootswatch()