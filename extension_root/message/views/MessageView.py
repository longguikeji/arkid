from django.db.models.query_utils import Q
from django.http import request
from common.paginator import DefaultListPaginator
from api.v1.views.base import BaseViewSet
from drf_spectacular.utils import extend_schema_view
from inventory.models import User
from openapi.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from ..models import Message
from ..serializers import BaseMessageSerializer, MessageSerializer, MessageInfoSerializer
from app.models import App
from django.http.response import JsonResponse


@extend_schema_view(
    list=extend_schema(
        responses=MessageInfoSerializer,
        roles=['tenant admin', 'global admin'],
    ),
    retrieve=extend_schema(roles=['tenant admin', 'global admin']),
    create=extend_schema(
        request=BaseMessageSerializer,
        roles=['tenant admin', 'global admin']
    ),
    update=extend_schema(
        request=BaseMessageSerializer,
        roles=['tenant admin', 'global admin']
    ),
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
class MessageViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = MessageInfoSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        qs = Message.active_objects.filter(
            app__tenant=tenant
        ).filter(
            Q(users=None) | Q(users=self.request.user)
        )
        
        type = self.request.GET.get("type",None)
        if type:
            qs = qs.filter(type=type)
        qs = qs.order_by('-id')
        return qs

    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']

        return (
            Message.active_objects.filter(
                app__tenant=tenant,
                uuid=uuid,
            )
            .order_by('id')
            .first()
        )

    def create(self, request, *args, **kwargs):
        app_uuid = request.data.get("app")
        app = App.active_objects.get(uuid=app_uuid)
        message = Message()
        message.app = app
        message.title = request.data.get("title", "")
        message.content = request.data.get("content", "")
        message.time = request.data.get("time", "")
        message.url = request.data.get("url", "")
        message.type = request.data.get("type", "")
        users_uuid = request.data.get("users", None)
        message.save()
        if users_uuid:
            message.users.set(
                User.active_objects.filter(
                    uuid__in=users_uuid
                ).all()
            )
        return JsonResponse(data={"status": 200, **(MessageSerializer(instance=message).data)})

    def update(self, request, *args, **kwargs):
        app_uuid = request.data.get("app")
        app = App.active_objects.get(uuid=app_uuid)
        message = self.get_object()
        message.app = app
        message.title = request.data.get("title", "")
        message.content = request.data.get("content", "")
        message.time = request.data.get("time", "")
        message.url = request.data.get("url", "")
        message.type = request.data.get("type", "")
        users_uuid = request.data.get("users", None)
        if users_uuid:
            message.users.clear()
            message.users.set(User.active_objects.filter(
                uuid__in=users_uuid).all())
        message.save()
        return JsonResponse(data={"status": 200, **(MessageSerializer(instance=message).data)})
