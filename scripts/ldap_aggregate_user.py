'''
OneID中组和部门都有层级关系，而LDAP中的group无法原生实现。
这里通过定期脚本，将子组中的成员添加到父组中，从而使得在查询中仍能提现出层级从属关系
'''
import re

from ldap3 import LEVEL

from ..oneid_meta.models import Dept, Group
from ..executer.utils.tree_node import dn_lrd_walker
from ..executer.LDAP.client import FILTER_ALL


def get_member_from_children(conn, dn):
    '''
    返回下级dn的所有成员
    下级是指dn路径上的下级
    成员是指member属性
    '''
    conn.search(dn, search_scope=LEVEL, search_filter=FILTER_ALL)
    all_members = set()
    for entry in conn.entries:
        members = conn.get_members(entry.entry_dn)
        all_members.update(members)
    return all_members


def aggregate_user_by_dn(conn, base_dn, cls):
    '''
    从下往上聚合dn成员
    LDAP当前节点成员 = LDAP下级节点成员之和 + RDB中查询得到的当前节点成员
    '''
    for dn in dn_lrd_walker(conn, base_dn):
        result = re.findall(r'^cn=([\w|_]+),', dn)
        if not result:
            continue
        uid = result[0]
        members = get_member_from_children(conn, dn)

        self_members = [user.dn for user in cls.valid_objects.get(uid=uid).users]

        members.update(self_members)

        conn.modify_soft_override(dn, 'member', members)


def aggregate_user_in_dept(conn, dept_base):
    '''
    从下往上聚合部门成员并逐节点保存
    '''
    return aggregate_user_by_dn(conn, base_dn=dept_base, cls=Dept)


def aggregate_user_in_group(conn, group_base):
    '''
    从下往上聚合组成员并逐节点保存
    '''
    return aggregate_user_by_dn(conn, base_dn=group_base, cls=Group)
