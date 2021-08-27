from openapi.utils import extend_schema_tags

tag = [ 'contacts_group', 'contacts_user' ]
path = 'contacts'
name = '通讯录'

contacts_group_tag = 'contacts_group'
contacts_group_name = '通讯录分组'

extend_schema_tags(
    contacts_group_tag,
    contacts_group_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contacts/group/',
            'method': 'get'
        },
        'local': {
            'children': {
                'path': '/api/v1/tenant/{tenant_uuid}/contacts/group/?parent={uuid}',
                'method': 'get'
            }
        }
    }
)

contacts_user_tag = 'contacts_user'
contacts_user_name = '通讯录'

extend_schema_tags(
    contacts_user_tag,
    contacts_user_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contacts/user/',
            'method': 'get'
        }
    }
)