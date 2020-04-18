'''
file upload && download
'''

import os
import uuid as uuid_utils
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.http.response import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.views.generic import View
from ...common.minio_utils import (
    put_object,
    presign_get,
)
from ...oneid_meta.models.config import StorageConfig


class FileCreateAPIView(generics.CreateAPIView):
    '''
    upload a file
    '''

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        '''
        upload file
        '''
        file = request.data.get('file')
        uuid = uuid_utils.uuid4().hex
        suffix = os.path.splitext(file.name)[1]
        file_name = uuid + suffix
        storage_config = StorageConfig.get_current()
        if storage_config.method == 'minio':
            put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=file_name,
                file_data=file,
                length=file.size,
            )
        else:
            with open(settings.UPLOADFILES_PATH + file_name, 'wb') as f:
                f.write(file.read())
        return Response({'file_name': file_name})


class FileAPIView(View):
    '''
    download the file
    '''

    permission_classes = []
    authentication_classes = []

    def get(self, request, filename):    # pylint: disable=unused-argument, no-self-use
        '''
        download file
        '''
        storage_config = StorageConfig.get_current()
        if storage_config.method == 'minio':
            url = presign_get(bucket_name=settings.MINIO_BUCKET,
                              object_name=filename,
                              response_headers={
                                  'response-content-disposition': 'attachment;filename=%s' % filename,
                              })
            return HttpResponseRedirect(url)

        filepath = settings.UPLOADFILES_PATH + filename
        if os.path.exists(filepath):
            data = open(filepath, 'rb').read()
            res = HttpResponse(data)
            res['Content-Type'] = 'application/octet-stream'
            res['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
            return res
        return HttpResponseNotFound()
