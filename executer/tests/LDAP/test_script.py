'''
test for LDAP scripts
'''
# pylint: disable=missing-docstring

import time
import string    # pylint: disable=deprecated-module
import random

from ....executer.tests.LDAP.test_executer import LDAPBaseTestCase, LDAPExecuterDeptTestCase
from ....siteapi.v1.tests.test_user import USER_DATA
from ....oneid_meta.models import UserPerm, Perm

from ....scripts.ldap_user_perm import flush_user_perm
from ....scripts.ldap_aggregate_user import aggregate_user_in_dept, aggregate_user_in_group


class PerformanceTestCase(LDAPBaseTestCase):
    def _test_replace_vals(self):
        vals = [f'{x}{y}' for x in string.ascii_lowercase for y in string.ascii_lowercase]
        keep_vals = [f'{x}{y}' for x in string.ascii_lowercase for y in string.digits]
        user = self.cli.create_user(USER_DATA)
        user_dn = user.dn
        self.conn.modify_add(user_dn, attribute='ou', vals=vals)    # length=26*26=676
        time_0 = time.time()
        for i in range(100):
            vals.pop(10 + i)
            vals.pop(300 + i)
            vals.append(keep_vals[50 + i])
            vals.append(keep_vals[100 + i])
            random.shuffle(vals)

            # case 1: replace:  # 4.005s
            # self.conn.modify_override(user_dn, attribute='ou', vals=vals)

            # case 2: add & delete  # 2.227s
            # self.conn.modify_soft_override(user_dn, attribute='ou', vals=vals)

        print(time.time() - time_0)
        print(self.conn.get_entry_by_dn(user.dn).entry_attributes_as_dict)


class UserPermTestCase(LDAPBaseTestCase):
    def test_flush_user_perm(self):
        user = self.cli.create_user(USER_DATA)
        for uid in string.ascii_lowercase:
            perm = Perm.valid_objects.create(uid=uid)
            user_perm = UserPerm.valid_objects.create(perm=perm, owner=user, value=True)

        perms = self.conn.get_vals(user.dn, 'ou')
        expect = []
        self.assertEqual(perms, expect)

        flush_user_perm(self.conn)

        perms = self.conn.get_vals(user.dn, 'ou')
        expect = list(string.ascii_lowercase)
        self.assertEqual(sorted(perms), expect)

        user_perm = UserPerm.valid_objects.get(owner=user, perm__uid='b')
        user_perm.value = False
        user_perm.save()

        self.conn.search('ou=people,dc=example,dc=org', '(ou=people)')
        self.conn.search('ou=people,dc=example,dc=org', '(ou=b)')
        self.assertEqual(len(self.conn.entries), 1)

        flush_user_perm(self.conn)

        expect = list(string.ascii_lowercase)
        expect.pop(expect.index('b'))
        perms = self.conn.get_vals(user.dn, 'ou')

        self.assertEqual(sorted(perms), expect)
        self.conn.search('ou=people,dc=example,dc=org', '(ou=b)')
        self.assertEqual(len(self.conn.entries), 0)


class UserAggregateTestCase(LDAPExecuterDeptTestCase):
    def test_aggregate_user_in_dept(self):
        expect = ['uid=employee_1,ou=people,dc=example,dc=org']
        self.assertEqual(self.conn.get_members(self.child_dept_1.dn), expect)
        expect = []
        self.assertEqual(self.conn.get_members(self.dept_1.dn), expect)
        self.assertEqual(self.conn.get_members(self.parent_dept.dn), expect)

        aggregate_user_in_dept(self.conn, 'ou=dept,dc=example,dc=org')
        expect = ['uid=employee_1,ou=people,dc=example,dc=org']
        self.assertEqual(self.conn.get_members(self.child_dept_1.dn), expect)
        self.assertEqual(self.conn.get_members(self.dept_1.dn), expect)
        self.assertEqual(self.conn.get_members(self.parent_dept.dn), expect)

    def test_aggregate_user_in_group(self):
        aggregate_user_in_group(self.conn, 'ou=group,dc=example,dc=org')
