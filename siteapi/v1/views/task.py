'''
entrypoint of scripts
'''

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django_celery_results.models import TaskResult

from oneid.permissions import CustomPerm, IsAdminUser, IsManagerUser
from siteapi.v1.serializers.user import UserListSerializer
from siteapi.v1.serializers.task import TaskResultSerializer
from docs.projects.noah.init import entrypoint as init_noah
from tasksapp.tasks import import_ding


class ImportDingAPIView(generics.RetrieveUpdateAPIView):
    '''
    拉取钉钉数据
    '''
    permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_account_sync'))]

    serializer_class = UserListSerializer

    def get(self, request, *args, **kwargs):
        task = import_ding.delay()
        return Response({'task_id': task.task_id, 'task_msg': 'import ding'})


class OverrideDingAPIView(generics.RetrieveUpdateAPIView):
    '''
    回写覆盖钉钉数据
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_account_sync'))]


class InitNoahAPIView(generics.RetrieveUpdateAPIView):
    '''
    init noah
    '''

    serializer_class = UserListSerializer

    def get(self, request, *args, **kwargs):
        '''
        init noah
        '''
        init_noah()
        return Response({'msg': 'inited'})


class TaskResultAPIView(generics.RetrieveAPIView):
    '''
    查询事件结果
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    serializer_class = TaskResultSerializer

    def get_object(self):
        result = TaskResult.objects.filter(task_id=self.kwargs['task_id']).first()
        if not result:
            raise NotFound
        return result
