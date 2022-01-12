from openapi.utils import extend_schema_tags

tag = [ 'group', 'group.user' ]
path = 'gmanage'
name = '分组管理'

group_tag = 'group'
group_name = '分组'

extend_schema_tags(
    group_tag,
    group_name,
    {
        'type':'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get',
            'next': 'group.user'
        },
        'global': {
            'create': {
                'tag': 'group.create',
                'description': '新建',
                'icon': 'el-icon-plus'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/group_import/',
                'method': 'post',
                'description': '导入',
                'icon': 'el-icon-upload2'
            },
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/group_export/',
                'method': 'get',
                'description': '导出',
                'icon': 'el-icon-download'
            }
        },
        'local': {
            'update': {
                'tag': 'group.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            },
            'node': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={id}',
                'method': 'get',
                'next': 'group.user'
            }
        }
    }
)

group_create_tag = 'group.create'
group_create_name = '创建组'

extend_schema_tags(
    group_create_tag,
    group_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

group_update_tag = 'group.update'
group_update_name = '编辑组'

extend_schema_tags(
    group_update_tag,
    group_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)

group_user_tag = 'group.user'
group_user_name = '组用户'

extend_schema_tags(
    group_user_tag,
    group_user_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/?group={group_uuid}',
            'method': 'get'
        },
        'global': {
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                'method': 'get',
                'description': '导出该组用户',
                'icon': 'el-icon-download'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                'method': 'post',
                'description': '导入',
                'icon': 'el-icon-upload2'
            }
        }
    }
)

group_tree_tag = 'group_tree'
group_tree_name = '分组'

extend_schema_tags(
    group_tree_tag,
    group_tree_name,
    {
        'type': 'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'local': {
            'node': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={id}',
                'method': 'get',
            }
        }
    }
)