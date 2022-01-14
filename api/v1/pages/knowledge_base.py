from openapi.utils import extend_schema_tags

tag = ['knowledge_base_manage']
path = 'knowledge_base_manage'
name = '知识驿站管理'

knowledge_base_manage_tag = 'knowledge_base_manage'
knowledge_base_manage_name = '知识驿站管理'

extend_schema_tags(
    knowledge_base_manage_tag,
    knowledge_base_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'knowledge_base_manage.create',
                'description': '创建新文章',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'knowledge_base_manage.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'description': '删除',
                'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/{id}/',
                'method': 'delete',
                'icon': 'el-icon-delete'
            },
            'retrive': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/{id}/read_record/',
                'method': 'get',
                'description': '已阅',
                'icon': 'el-icon-reading'
            },
        }
    }
)

knowledge_base_manage_create_tag = 'knowledge_base_manage.create'
knowledge_base_manage_create_name = '创建新文章'

extend_schema_tags(
    knowledge_base_manage_create_tag,
    knowledge_base_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

knowledge_base_manage_update_tag = 'knowledge_base_manage.update'
knowledge_base_manage_update_name = '编辑文章'

extend_schema_tags(
    knowledge_base_manage_update_tag,
    knowledge_base_manage_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/knowledge_base_article/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
