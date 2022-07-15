from arkid.core.approve import create_approve_action

create_approve_action('添加用户权限', '/api/v1/mine/tenant/{tenant_id}/permissions/{permission_id}/add_permisssion', 'GET')