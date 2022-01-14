from openapi.utils import extend_schema_tags
from django.conf import settings
from extension.models import Extension
from django.utils.translation import ugettext_lazy as _

tag = ['desktop', 'article']
path = 'desktop'
name = '桌面'

app_tag = 'desktop'
app_name = '应用市集'

extend_schema_tags(
        app_tag,
        app_name,
        {
            'type': 'list_page',
            'init': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{parent_lookup_user}/app/',
                'method': 'get'
            },
            'global': {
                'manage':{
                    'tag': 'app_manage',
                    'description': '管理应用'      
                }
            }
        }
    )

app_manage_tag = 'app_manage'
app_manage_name = '管理应用'

extend_schema_tags(
    app_manage_tag,
    app_manage_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{parent_lookup_user}/app_subscribe_list/',
            'method': 'get'
        },
        'local': {
            'item': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/user/{parent_lookup_user}/subscribe/',
                'method': 'post'
            }
        }
    }
)

article_tag = 'article'
article_name = '知识驿站'

extend_schema_tags(
    article_tag,
    article_name,
    {
        'type': 'list_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/',
            'method': 'get'
        }
    }
)
