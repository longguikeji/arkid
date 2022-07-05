from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import api as core_api, event as core_event

class AuthRegularBaseExtension(Extension):

    TYPE = "auth_regular"

    @property
    def type(self):
        return AuthRegularBaseExtension.TYPE

    def load(self):
        super().load()