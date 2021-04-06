from openapi.utils import extend_schema_tags

tag = 'group'
path = tag
name = '分组管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'tree_page',
        'treeList': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'treeCreate': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'post'
        },
        'treeUpdate': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
            'method': 'put'
        },
        'treeDelete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
            'method': 'delete'
        },
        'childrenList': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={id}',
            'method': 'get'
        },
        'tableList': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/?group={id}',
            'method': 'get'
        },
        'tableUpdate': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'put'
        },
        'tableDelete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
            'method': 'delete'
        }
    }
)