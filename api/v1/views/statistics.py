from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openapi.utils import extend_schema
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from perm.custom_access import ApiAccessPermission
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from tenant.models import Tenant
from runtime import get_app_runtime


CACHE_SECONDS = 60*2


@extend_schema(
    roles=['tenantadmin', 'globaladmin', 'statisticalgraph'],
    summary='统计图表',
    tags=['statistics'],
)
class StatisticsView(APIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @method_decorator(cache_page(CACHE_SECONDS))
    def get(self, request, *args, **kwargs):
        tenant_uuid = kwargs.get('tenant_uuid')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        charts = []
        r = get_app_runtime()
        if r.statistics_provider:
            charts = r.statistics_provider.get_charts(tenant)
        return Response(charts)
