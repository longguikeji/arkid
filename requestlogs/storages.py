import json
import logging

from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers
from rest_framework.utils.encoders import JSONEncoder

from .base import SETTINGS
from .utils import chunk_to_max_len


logger = logging.getLogger('requestlogs')


class JsonDumpField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, dict):
            for field_name, field_value in value.items():
                if isinstance(field_value, UploadedFile):
                    value[field_name] = (
                        f'<{field_value.__class__.__name__}, size={field_value.size}>')
        data = json.dumps(value, cls=JSONEncoder)
        return chunk_to_max_len(data)


class BaseRequestSerializer(serializers.Serializer):
    method = serializers.CharField(read_only=True)
    full_path = serializers.CharField(read_only=True)
    path = serializers.CharField(read_only=True)
    data = JsonDumpField(read_only=True)
    query_params = JsonDumpField(read_only=True)


class BaseEntrySerializer(serializers.Serializer):
    class ResponseSerializer(serializers.Serializer):
        status_code = serializers.IntegerField(read_only=True)
        data = JsonDumpField(read_only=True)

    class UserSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        username = serializers.CharField()

    action_name = serializers.CharField(read_only=True)
    execution_time = serializers.DurationField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    ip_address = serializers.CharField(read_only=True)
    request = BaseRequestSerializer(read_only=True)
    response = ResponseSerializer(read_only=True)
    user = UserSerializer()


class RequestIdEntrySerializer(BaseEntrySerializer):
    class RequestSerializer(BaseRequestSerializer):
        request_id = serializers.CharField()

    request = RequestSerializer()


class BaseStorage(object):
    serializer_class = None

    def get_serializer_class(self):
        return (self.serializer_class if self.serializer_class else
                SETTINGS['SERIALIZER_CLASS'])

    def prepare(self, entry):
        return self.get_serializer_class()(entry).data


class LoggingStorage(BaseStorage):
    def store(self, entry):
        logger.info(self.prepare(entry))
