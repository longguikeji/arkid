from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from tenant.models import Tenant
from inventory.models import User
from rest_framework_extensions.settings import extensions_api_settings


class BaseTenantViewSet(NestedViewSetMixin):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        k: str = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'tenant'
        u: str = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'user'

        if k in self.kwargs:
            context['tenant'] = Tenant.objects.filter(uuid=self.kwargs[k]).first()
        if u in self.kwargs:
            context['user'] = User.objects.filter(uuid=self.kwargs[u]).first()

        return context


class BaseViewSet(BaseTenantViewSet, viewsets.ModelViewSet):

    pass
