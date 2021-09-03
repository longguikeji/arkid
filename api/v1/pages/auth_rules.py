from openapi.utils import extend_schema_tags

tag = 'auth_rules'
path = tag
name = '认证规则'

extend_schema_tags(
    tag,
    name,
    # {
    #     'type':'table_page',
    #     'init': {
    #         'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/',
    #         'method': 'get'
    #     },
    #     'global': {
    #         'create': {
    #             'tag': 'auth_rules.create'
    #         }
    #     }
    # }
)

# auth_rule_create_tag = "auth_rules.create"
# auth_rule_create_name = "添加认证规则"

# extend_schema_tags(
#     auth_rule_create_tag,
#     auth_rule_create_name,
#     {
#         'type': 'form_page',
#         'init': {
#             'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/',
#             'method': 'post'
#         },
#         'global': {
#             'create': {
#                 'path': '/api/v1/tenant/{parent_lookup_tenant}/auth_rule/',
#                 'method': 'post'
#             }
#         }
#     }
# )