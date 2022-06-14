#!/usr/bin/env python3

from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig


class AccountLifeExtension(Extension):

    TYPE = "account_life"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return AccountLifeExtension.TYPE

    def load(self):
        super().load()
        self.listen_event(
            core_event.ACCOUNT_LIFE_PERIODIC_TASK, self.periodic_task_event_handler
        )

    @abstractmethod
    def periodic_task(self, event, **kwargs):
        """
        抽象方法
        Args:
            event (arkid.core.event.Event):  生命周期定时任务事件
        """
        pass

    def periodic_task_event_handler(self, event, **kwargs):
        self.periodic_task(event, **kwargs)

    def register_account_life_schema(self, schema, config_type):
        self.register_config_schema(schema, self.package + '_' + config_type)
        self.register_composite_config_schema(
            schema, config_type, exclude=['extension']
        )
