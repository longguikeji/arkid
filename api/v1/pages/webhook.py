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
        'global': {
            'create': {
                'tag': 'webhook.create',
                'description': '添加Webhook',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'history': {
                'tag': 'webhook.history',
                'description': '历史记录',
                'icon': 'el-icon-reading'
            },
            'update': {
                'tag': 'webhook.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

webhook_create_tag = 'webhook.create'
webhook_create_name = '添加Webhook'

extend_schema_tags(
    webhook_create_tag,
    webhook_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

webhook_update_tag = 'webhook.update'
webhook_update_name = '编辑Webhook'

extend_schema_tags(
    webhook_update_tag,
    webhook_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
                'method': 'put',
                'description': '确定'
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
        'local': {
            'retrieve': {
                'tag': 'webhook.history.retrieve',
                'description': '查阅',
                'icon': 'el-icon-tickets'
            },
            'retry': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/{id}/retry/',
                'method': 'get',
                'description': '重复该操作',
                'icon': 'el-icon-d-arrow-right'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
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
