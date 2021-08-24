from openapi.utils import extend_schema_tags

tag = 'contacts_user_config'
path = tag
name = '个人字段可见性'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/info_visibility/',
            'method': 'get'
        },
        'local': {
            'update': {
                'tag': 'contacts_user_config.update'
            }
        }
    }
)

contacts_info_visibility_update_tag = 'contacts_user_config.update'
contacts_info_visibility_update_name = '编辑通讯录个人字段可见性'

extend_schema_tags(
    contacts_info_visibility_update_tag,
    contacts_info_visibility_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/info_visibility/{info_uuid}/detail/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/info_visibility/{info_uuid}/detail/',
                'method': 'put'
            }
        }
    }
)