from openapi.utils import extend_schema_tags

tag = 'webhook'
path = tag
name = 'Webhook'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'webhook.create'
            }
        },
        'item': {
            'history': {
                'tag': 'webhook.history'
            },
            'update': {
                'tag': 'webhook.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
                'method': 'delete'
            }
        }
    }
)

webhook_create_tag = 'webhook.create'
webhook_create_name = '创建webhook'

extend_schema_tags(
    webhook_create_tag,
    webhook_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
                'method': 'post',
            }
        }
    }
)

webhook_update_tag = 'webhook.update'
webhook_update_name = '编辑更新webhook'

extend_schema_tags(
    webhook_update_tag,
    webhook_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
                'method': 'put'
            }
        }
    }
)

webhook_history_tag = 'webhook.history'
webhook_history_name = 'webhook历史记录'

extend_schema_tags(
    webhook_history_tag,
    webhook_history_tag,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/',
            'method': 'get'
        },
        'item': {
            'retrieve': {
                'tag': 'webhook.history.retrieve'
            },
            'retry': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/{id}/retry/',
                'method': 'get'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/{id}/',
                'method': 'delete'
            }
        }
    }
)

webhook_history_retrieve_tag = 'webhook.history.retrieve'
webhook_history_retrieve_name = 'webhook历史记录查阅'

extend_schema_tags(
    webhook_history_retrieve_tag,
    webhook_history_retrieve_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/{id}/',
            'method': 'get'
        }
    }
)