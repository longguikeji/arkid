'''
views for advanced feature
- plugin
- ...
'''
import pathlib
import os

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.conf import settings

from oneid_meta.models import CrontabPlugin
from siteapi.v1.serializers.advance import CrontabPluginSerializer
from oneid.permissions import IsAdminUser


class CrontabPluginListAPIView(generics.ListAPIView):
    '''
    crontab 插件列表
    自动收集指定目录下的crontab插件
    '''

    permission_classes = [IsAdminUser]
    serializer_class = CrontabPluginSerializer

    def get(self, request, *args, **kwargs):
        base_dir = pathlib.Path(settings.BASE_DIR)
        workspace = base_dir / 'plugins' / 'crontab'
        plugin_paths = set()
        for (dirpath, _, filenames) in os.walk(workspace):
            for filename in filenames:
                if filename.endswith('.py'):
                    plugin_paths.add(str(
                        (pathlib.Path(dirpath) / filename.replace('.py', '')).\
                        relative_to(base_dir)
                    ).replace('/', '.') + '.main')
        for plugin in CrontabPlugin.valid_objects.all():
            if plugin.import_path not in plugin_paths:
                plugin.delete()
            else:
                plugin_paths.pop()

        for plugin_path in plugin_paths:
            CrontabPlugin.valid_objects.create(
                name=plugin_path,
                import_path=plugin_path,
                is_active=False,
            )

        return Response(self.get_serializer(CrontabPlugin.valid_objects.all(), many=True).data)


class CrontabPluginDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
    crontab 插件详情
    '''

    permission_classes = [IsAdminUser]
    serializer_class = CrontabPluginSerializer

    def get_object(self):
        '''
        find plugin by uuid
        '''
        instance = CrontabPlugin.valid_objects.filter(uuid=self.kwargs['uuid']).first()
        if not instance:
            raise NotFound
        return instance


class MiddlewarePluginListAPIView(generics.ListCreateAPIView):
    '''
    middleware 插件列表
    '''


class MiddlewarePluginDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    middleware 插件详情
    '''
