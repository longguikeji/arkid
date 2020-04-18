'''
user的权限可以独立于组、部门另外自行设置
因此LDAP中基于group的查询并不能完全读取到OneID中的权限配置
为使OneID中的权限数据能通过LDAP充分暴露，另外在inetOrgPerson的ou属性中维护用户所拥有的所有权限

即一方面可以通过group进行管理，也可以直接针对具体权限管理

暂不打算将组、部门的权限通过LDAP暴露
'''

from ..oneid_meta.models import User, UserPerm


def flush_user_perm(conn, users=None):
    '''
    LDAP中维护用户权限
    '''
    if users is None:
        users = User.valid_objects.all()

    for user in users:
        user_dn = user.dn
        valid_perm_uids = UserPerm.valid_objects.filter(owner=user, value=True).values_list('perm__uid', flat=True)
        if not valid_perm_uids:
            continue

        conn.modify_soft_override(user_dn, 'ou', valid_perm_uids)
