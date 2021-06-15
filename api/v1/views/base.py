from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from tenant.models import Tenant
from inventory.models import User
from app.models import App
from provisioning.models import Config
from rest_framework_extensions.settings import extensions_api_settings


class BaseTenantViewSet(NestedViewSetMixin):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        k: str = (
            extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'tenant'
        )
        u: str = (
            extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'user'
        )
        a: str = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'app'
        p: str = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'provisioning'

        if k in self.kwargs:
            context['tenant'] = Tenant.objects.filter(uuid=self.kwargs[k]).first()
        if u in self.kwargs:
            context['user'] = User.objects.filter(uuid=self.kwargs[u]).first()
        if a in self.kwargs:
            context['app'] = App.objects.filter(uuid=self.kwargs[a]).first()
        if p in self.kwargs:
            context['provisioning'] = Config.objects.filter(uuid=self.kwargs[p]).first()

        return context


class BaseViewSet(BaseTenantViewSet, viewsets.ModelViewSet):

    pass
