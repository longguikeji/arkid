from tenant.models import Tenant
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.paginator import DefaultListPaginator
from app.models import App

class AuthRuleAppChoicesListView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    pagination_class = DefaultListPaginator

    def get_queryset(self):

        tenant = self.request.query_params.get('tenant', None)

        apps = App.active_objects

        if tenant:
            apps = apps.filter(tenant__uuid=tenant)

        return [
            {
                "name": app.name,
                "value": app.id
            } for app in apps.all()
        ]