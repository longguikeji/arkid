"""
知识库文章视图
"""
from django.http.response import JsonResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from openapi.utils import extend_schema
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.decorators import action
from common.paginator import DefaultListPaginator
from common.code import Code
from api.v1.views.base import BaseViewSet
from ..models import Article
from ..serializers import BaseArticleSerializer


@extend_schema_view(
    list=extend_schema(
        roles=['tenant admin', 'global admin', 'general user'],
        responses=BaseArticleSerializer,
        parameters=[
            OpenApiParameter(
                name='created__gte',
                type={'type': 'datetime'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='created__lte',
                type={'type': 'datetime'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='author__username',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ]
    ),
    retrieve=extend_schema(roles=['tenant admin', 'global admin']),
    create=extend_schema(roles=['tenant admin', 'global admin']),
    update=extend_schema(roles=['tenant admin', 'global admin']),
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags=['app'],
)
class ArticleViewSet(BaseViewSet):
    """
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = BaseArticleSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        qs = Article.active_objects.all().order_by('-id')
        return qs

    def get_object(self):
        print(self.kwargs)
        uuid = self.kwargs['pk']

        return Article.active_objects.filter(
            uuid=uuid,
        ).order_by('id').first()

    def create(self, request, *args, **kwargs):

        article = Article(
            title=request.data.get("title"),
            content=request.data.get("content"),
            author=request.user,

        )
        article.save()

        return JsonResponse(
            data={
                'status': 200
            }
        )

    @action(detail=True, methods=['get'])
    def read_record(self, request, parent_lookup_tenant=None, pk=None):
        article = self.get_object()
        article.read_record(request.user)
        return JsonResponse(
            data={
                'status': 200
            }
        )
