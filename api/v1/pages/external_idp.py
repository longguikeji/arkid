from openapi.utils import extend_schema_tags

tag = 'external_idp'
path = tag
name = '第三方登录'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'list': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/',
            'method': 'get',
        },
        'create': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/',
            'method': 'post',
        },
        'update': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/',
            'method': 'put',
        },
        'delete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/',
            'method': 'delete',
        },
        'sort': {
            'up': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_up/',
                'method': 'get',
            },
            'down': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_down/',
                'method': 'get',
            },
            'top': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_top/',
                'method': 'get',
            },
            'bottom': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/{id}/move_bottom/',
                'method': 'get',
            },
            'batch': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/external_idp/batch_update/',
                'method': 'post',
            },
        },
    },
)
