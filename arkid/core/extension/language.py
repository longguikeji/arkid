
from abc import abstractmethod
from arkid.common.logger import logger
from ninja import Schema
from typing import List, Optional, Literal
from pydantic import Field
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.models import LanguageData
from arkid.core import translation as core_translation


class LanguageExtension(Extension):

    TYPE = "language"

    @property
    def type(self):
        return LanguageExtension.TYPE

    def load(self):
        super().load()
        self.load_language_data(
            language_type=self.language_type(),
            data=self.language_data()
        )

    def load_language_data(self, data, language_type=_("简体中文")):
        """加载语言包

        Args:
            data (dict): 翻译数据
            language_type (str, optional): 语言名称. Defaults to _("简体中文").
        """

        self.language_type = language_type
        self.extension_data = data

        extension = self.model
        try:
            language_data, _ = LanguageData.active_objects.get_or_create(
                extension=extension)
            language_data.extension_data = self.extension_data
            language_data.name = self.language_type

            language_data.save()
        except Exception as err:
            logger.error(err)

        self.refresh_lang_maps()

    @abstractmethod
    def language_type(self) -> str:
        """ 语言类型

        Returns:
            str: 语言类型名称 默认为简体中文
        """
        return _("简体中文")

    @abstractmethod
    def language_data(self) -> dict:
        """翻译数据

        Returns:
            dict: 翻译数据字典
        """
        return {}

    def refresh_lang_maps(self):
        """刷新语言包
        """
        core_translation.lang_maps = core_translation.reset_lang_maps()
