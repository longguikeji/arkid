from openapi.utils import extend_schema_tags

tag = 'contacts_switch'
path = tag
name = '通讯录开关'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/function_switch/',
            'method': 'get'
        },
        'global': {
            'update': {
                'tag': 'contacts_switch.update'
            }
        }
    }
)

contacts_switch_update_tag = 'contacts_switch.update'
contacts_switch_update_name = '编辑通讯录开关'

extend_schema_tags(
    contacts_switch_update_tag,
    contacts_switch_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/function_switch/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/function_switch/',
                'method': 'put'
            }
        }
    }
)
