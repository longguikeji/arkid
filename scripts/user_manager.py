'''
用户管理
'''

from ..oneid_meta.models import User


def rm_unbonded_user():
    '''
    删除不属于任何部门的用户
    '''
    for user in User.valid_objects.exclude(username='admin'):
        if not user.depts:
            user.delete()
