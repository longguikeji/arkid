'''
views about log
'''

import datetime

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from django.db.models import Q

from ....oneid_meta.models import Log
from ....oneid.permissions import CustomPerm, IsAdminUser
from ....siteapi.v1.serializers.log import LogSerializer, LogLiteSerializer
from ....common.django.drf.paginator import DefaultListPaginator


class LogListAPIView(generics.ListAPIView):
    '''
    get log list [GET]
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_log_read'))]

    serializer_class = LogLiteSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        '''
        filter queryset
        '''
        kwargs = {}

        subject = self.request.query_params.get('subject', '')
        if subject:
            kwargs['subject__in'] = subject.split('|')

        summary = self.request.query_params.get('summary', '')
        if summary:
            kwargs['summary__icontains'] = summary

        days = self.request.query_params.get('days', None)
        if days is not None:
            if not days.isdigit():
                raise ValidationError({'days': ['this field must be interger']})
            days = int(days)

            now = timezone.now()
            if days == 0:
                local_now = timezone.localtime(now)
                kwargs['created__gte'] = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                kwargs['created__gte'] = now - datetime.timedelta(days=days)

        queryset = Log.objects.filter(**kwargs)

        user = self.request.query_params.get('user', '')
        if user:
            queryset = queryset.filter(Q(user__username__icontains=user) | Q(user__name__icontains=user))

        return queryset.order_by('-created')


class LogDetailAPIView(generics.RetrieveAPIView):
    '''
    get log detail [GET]
    '''

    serializer_class = LogSerializer

    def get_object(self):
        '''
        retrieve object
        '''
        log = Log.objects.filter(uuid=self.kwargs['uuid']).first()
        if not log:
            raise NotFound

        return log


class MetaLogAPIView(generics.ListAPIView):
    '''
    get log meta [GET]
    '''
    def get_queryset(self):
        for key, val in Log.SUBJECT_CHOICES.items():
            yield {
                'subject': key,
                'name': val,
            }

    def get(self, request, *args, **kwargs):
        return Response(self.get_queryset())
