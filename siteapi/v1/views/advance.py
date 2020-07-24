'''
views for advanced feature
- plugin
- ...
'''
import pathlib
import os
from inspect import getmembers, isfunction

from celery import Task
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.conf import settings
from django.utils.module_loading import import_string

from oneid_meta.models import CrontabPlugin, MiddlewarePlugin
from siteapi.v1.serializers.advance import CrontabPluginSerializer, MiddlewarePluginSerializer
from oneid.permissions import IsAdminUser


def collect_plugins(workspace, p_type):
    '''
    在指定目录下寻找所有符合条件的插件，以路径形式返回
    - python function
    - endswith '_plugin'
    '''
    base_dir = pathlib.Path(settings.BASE_DIR)
    for (dirpath, _, filenames) in os.walk(workspace):
        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            module_path = str((pathlib.Path(dirpath) / filename.replace('.py', '')).\
                relative_to(base_dir)).replace('/', '.')

            __import__(module_path)
            for name, obj in getmembers(import_string(module_path)):
                if name.endswith('_plugin'):
                    if p_type == 'crontab' and isinstance(obj, Task):
                        yield '.'.join([module_path, name])
                    if p_type == 'middleware' and isfunction(obj):
                        yield '.'.join([module_path, name])


class CrontabPluginListAPIView(generics.ListAPIView):
    '''
    crontab 插件列表
    自动收集指定目录下的crontab插件
    '''

    permission_classes = [IsAdminUser]
    serializer_class = CrontabPluginSerializer

    def get(self, request, *args, **kwargs):
        workspace = pathlib.Path(settings.BASE_DIR) / 'plugins' / 'crontab'
        plugin_paths = set(collect_plugins(workspace, 'crontab'))

        for plugin in CrontabPlugin.objects.all():
            if plugin.import_path not in plugin_paths:
                # 清理DB中已删除的插件记录
                plugin.delete()
            else:
                # 过滤已存在的插件记录
                plugin_paths.remove(plugin.import_path)

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
    TODO: 排序
    '''
    permission_classes = [IsAdminUser]
    serializer_class = MiddlewarePluginSerializer

    def get(self, request, *args, **kwargs):
        workspace = pathlib.Path(settings.BASE_DIR) / 'plugins' / 'middleware'
        plugin_paths = set(collect_plugins(workspace, 'middleware'))

        for plugin in MiddlewarePlugin.valid_objects.all():
            if plugin.import_path not in plugin_paths:
                plugin.delete()
            else:
                plugin_paths.pop()

        for plugin_path in plugin_paths:
            MiddlewarePlugin.valid_objects.create(
                name=plugin_path,
                import_path=plugin_path,
                is_active=False,
            )

        return Response(self.get_serializer(MiddlewarePlugin.valid_objects.all(), many=True).data)


class MiddlewarePluginDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    middleware 插件详情
    '''

    permission_classes = [IsAdminUser]
    serializer_class = MiddlewarePluginSerializer

    def get_object(self):
        '''
        find plugin by uuid
        '''
        instance = MiddlewarePlugin.valid_objects.filter(uuid=self.kwargs['uuid']).first()
        if not instance:
            raise NotFound
        return instance
