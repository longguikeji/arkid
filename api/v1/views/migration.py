from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from runtime import get_app_runtime
from api.v1.serializers.migration import MigrationSerializer


class MigrationAPIView(APIView):

    serializer_class = MigrationSerializer

    @property
    def migration_provider(self):
        r = get_app_runtime()

        migration_provider = r.migration_provider
        assert migration_provider is not None
        return migration_provider

    def post(self, request):
        if 'tenant_uuid' not in request.data:
            raise ParseError("Empty content")

        tenant_uuid = request.data['tenant_uuid']
        self.migration_provider.migrate(tenant_uuid)
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'error': '0',
            },
        )
