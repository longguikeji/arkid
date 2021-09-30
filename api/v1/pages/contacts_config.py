from openapi.utils import extend_schema_tags

tag = [ 'contacts_switch', 'contacts_group_config', 'contacts_user_config' ]
path = 'contacts_config'
name = '通讯录设置'

contacts_switch_tag = 'contacts_switch'
contacts_switch_name = '通讯录开关'

extend_schema_tags(
    contacts_switch_tag,
    contacts_switch_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/function_switch/',
            'method': 'get'
        },
        'local': {
            'item': {
                'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/function_switch/',
                'method': 'put'
            }
        }
    }
)

contacts_group_visibility_tag = 'contacts_group_config'
contacts_group_visibility_name = '组的可见性'

extend_schema_tags(
    contacts_group_visibility_tag,
    contacts_group_visibility_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'local': {
            'update': {
                'tag': 'contacts_group_config.update',
                'description': '设置可见性',
                'icon': 'el-icon-setting'
            }
        },
        'node': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={uuid}',
            'method': 'get'
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
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

contacts_info_visibility_tag = 'contacts_user_config'
contacts_info_visibility_name = '个人字段可见性'

extend_schema_tags(
    contacts_info_visibility_tag,
    contacts_info_visibility_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/contactsconfig/info_visibility/',
            'method': 'get'
        },
        'local': {
            'update': {
                'tag': 'contacts_user_config.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
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
                'method': 'put',
                'description': '确定'
            }
        }
    }
)