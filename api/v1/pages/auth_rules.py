from openapi.utils import extend_schema_tags

tag = 'auth_rules'
path = tag
name = '认证规则'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'auth_rules.create',
                'description': '添加认证规则',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'auth_rules.update',
                'description': '编辑认证规则',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        },
    }
)

auth_rule_create_tag = "auth_rules.create"
auth_rule_create_name = "添加认证规则"

extend_schema_tags(
    auth_rule_create_tag,
    auth_rule_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)


auth_rules_update_tag = 'auth_rules.update'
auth_rules_update_name = '编辑认证规则'

extend_schema_tags(
    auth_rules_update_tag,
    auth_rules_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
