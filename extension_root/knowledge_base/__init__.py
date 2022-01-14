from .extension import KnowledgeBaseExtension
from django.utils.translation import ugettext_lazy as _


extension = KnowledgeBaseExtension(
    scope='global',
    type='global',
    name='knowledge_base',
    tags='article',
    description=_('知识库'),
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='support@longguikeji.com',
)
