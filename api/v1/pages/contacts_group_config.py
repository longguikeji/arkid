from openapi.utils import extend_schema_tags

tag = 'contacts_group_config'
path = tag
name = '组的可见性'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'local': {
            'update': {
                'tag': 'contacts_group_config.update',
                'description': '设置可见性'
            },
            'children': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={uuid}',
                'method': 'get'
            }
        }
    }
)

contacts_group_visibility_update_tag = 'contacts_group_config.update'
contacts_group_visibility_update_name = '编辑通讯录分组可见性'

extend_schema_tags(
    contacts_group_visibility_update_tag,
    contacts_group_visibility_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/{group_uuid}/group_visibility/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/{group_uuid}/group_visibility/',
                'method': 'put'
            }
        }
    }
)
