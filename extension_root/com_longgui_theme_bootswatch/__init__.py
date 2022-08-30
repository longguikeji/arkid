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
        self.register_front_theme('cerulean', 'https://bootswatch.com/5/cerulean/bootstrap.min.css')
        self.register_front_theme('cosmo', 'https://bootswatch.com/5/cosmo/bootstrap.min.css')
        self.register_front_theme('cyborg', 'https://bootswatch.com/5/cyborg/bootstrap.min.css')
        self.register_front_theme('flatly', 'https://bootswatch.com/5/flatly/bootstrap.min.css')
        self.register_front_theme('journal', 'https://bootswatch.com/5/journal/bootstrap.min.css')
        self.register_front_theme('litera', 'https://bootswatch.com/5/litera/bootstrap.min.css')
        self.register_front_theme('lumen', 'https://bootswatch.com/5/lumen/bootstrap.min.css')
        self.register_front_theme('lux', 'https://bootswatch.com/5/lux/bootstrap.min.css')
        self.register_front_theme('minty', 'https://bootswatch.com/5/minty/bootstrap.min.css')
        self.register_front_theme('morph', 'https://bootswatch.com/5/morph/bootstrap.min.css')
        self.register_front_theme('pulse', 'https://bootswatch.com/5/pulse/bootstrap.min.css')
        self.register_front_theme('quartz', 'https://bootswatch.com/5/quartz/bootstrap.min.css')
        self.register_front_theme('sandstone', 'https://bootswatch.com/5/sandstone/bootstrap.min.css')
        self.register_front_theme('simplex', 'https://bootswatch.com/5/simplex/bootstrap.min.css')
        self.register_front_theme('sketchy', 'https://bootswatch.com/5/sketchy/bootstrap.min.css')
        self.register_front_theme('slate', 'https://bootswatch.com/5/slate/bootstrap.min.css')
        self.register_front_theme('solar', 'https://bootswatch.com/5/solar/bootstrap.min.css')
        self.register_front_theme('spacelab', 'https://bootswatch.com/5/spacelab/bootstrap.min.css')
        self.register_front_theme('superhero', 'https://bootswatch.com/5/superhero/bootstrap.min.css')
        self.register_front_theme('united', 'https://bootswatch.com/5/united/bootstrap.min.css')
        self.register_front_theme('vapor', 'https://bootswatch.com/5/vapor/bootstrap.min.css')
        self.register_front_theme('zephyr', 'https://bootswatch.com/5/zephyr/bootstrap.min.css')
        return super().load()


extension = ThemeBootswatch()