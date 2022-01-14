from extension_root.knowledge_base.views import (
    ArticleViewSet as view_article
)

from .tenant import tenant_router


tenant_ticket_router = tenant_router.register(
    r'knowledge_base_article', view_article, basename='tenant-knowledge_base-article', parents_query_lookups=['tenant'])
