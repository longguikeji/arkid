from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from runtime import get_app_runtime
from api.v1.serializers.storage import UploadSerializer


class UploadAPIView(APIView):

    serializer_class = UploadSerializer

    @property
    def storage_provider(self):
        r = get_app_runtime()

        storage_provider = r.storage_provider
        assert storage_provider is not None
        return storage_provider

    def post(self, request):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        uploaded_file = request.data['file']

        key = self.storage_provider.upload(uploaded_file)
        return Response(status=status.HTTP_201_CREATED, data={
            'key': key,
        })