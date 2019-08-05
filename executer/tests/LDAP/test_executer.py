'''
tests for basic LDAP operators
- create user
- create dept
- create group
- add users to dept
- add users to group
'''
# pylint: disable=missing-docstring

from django.test import TestCase
from django.conf import settings
from ldap3 import Server
from ldap3.core.exceptions import (
    LDAPNotAllowedOnNotLeafResult,
    LDAPUnwillingToPerformResult,
)

from executer.core import cli_factory
from executer.LDAP import LDAPExecuter
from executer.RDB import RDBExecuter
from executer.tests import (
    DEPT_DATA,
    PARENT_DEPT_DATA,
    GROUP_DATA,
    PARENT_GROUP_DATA,
    CHILD_DEPT_1_DATA,
    CHILD_DEPT_2_DATA,
    DEPT_2_DATA,
)
from executer.LDAP.client import Connection
from siteapi.v1.tests.test_user import USER_DATA
from oneid_meta.models import Dept, Group, User


class LDAPBaseTestCase(TestCase):

    maxDiff = None

    def __init__(self, *args, **kwargs):
        self.server = Server(settings.LDAP_SERVER)
        self.base = settings.LDAP_BASE
        self.conn = Connection(self.server,
                               user=settings.LDAP_USER,
                               password=settings.LDAP_PASSWORD,
                               auto_bind=True,
                               raise_exceptions=False)
        self.ldap_executer = LDAPExecuter(base='dc=example,dc=org')
        self.rdb_executer = RDBExecuter()
        self.cli = cli_factory([
            'executer.RDB.RDBExecuter',
            'executer.LDAP.LDAPExecuter',
        ])(User.objects.first())
        settings.LDAP_BASE = 'dc=example,dc=org'
        super(LDAPBaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.tearDown()
        self.conn.add('ou=people,{}'.format(self.base), 'organizationalUnit')
        self.conn.add('ou=group,{}'.format(self.base), 'organizationalUnit')
        self.conn.add('ou=dept,{}'.format(self.base), 'organizationalUnit')

    def tearDown(self):
        self.conn.force_delete('ou=people,{}'.format(self.base))
        self.conn.force_delete('ou=group,{}'.format(self.base))
        self.conn.force_delete('ou=dept,{}'.format(self.base))


class LDAPServerTestCase(LDAPBaseTestCase):
    def test_support_for_memberof(self):
        user = self.cli.create_user(USER_DATA)

        dept = self.cli.create_dept(DEPT_DATA)
        self.cli.add_dept_to_dept(dept, Dept.valid_objects.get(uid='root'))

        self.cli.add_users_to_dept([user], dept)

        self.conn.search(user.dn, '(objectClass=*)', attributes='memberOf')
        self.assertEqual(
            self.conn.entries[0].entry_attributes_as_dict['memberOf'],
            ['cn=dev,ou=dept,dc=example,dc=org'],
        )


class LDAPExecuterBasicTestCase(LDAPBaseTestCase):
    def test_add_user(self):
        dn = self.ldap_executer.create_user(USER_DATA)
        expect = {
            'gidNumber': [500],
            'displayName': ['employee_1'],
            'uidNumber': [500],
            'mobile': ['18812345678'],
            'homeDirectory': ['.'],
            'objectClass': ['inetOrgPerson', 'shadowAccount', 'posixAccount', 'ldapPublicKey'],
            'mail': ['email'],
            'cn': ['employee_1'],
            'uid': ['employee_1'],
            'sn': ['employee_1'],
        }
        self.assertEqual(self.conn.get_entry_by_dn(dn).entry_attributes_as_dict, expect)

    def test_update_user(self):
        user = self.rdb_executer.create_user(USER_DATA)
        dn = self.ldap_executer.create_user(USER_DATA)
        update_data = {
            'email': 'new_email',
            'posix_user': {
                'uid': 507,
            },
        }
        self.ldap_executer.update_user(user, update_data)
        expect = {
            'gidNumber': [500],
            'displayName': ['employee_1'],
            'uidNumber': [507],
            'mobile': ['18812345678'],
            'homeDirectory': ['.'],
            'objectClass': ['inetOrgPerson', 'shadowAccount', 'posixAccount', 'ldapPublicKey'],
            'mail': ['new_email'],
            'cn': ['employee_1'],
            'uid': ['employee_1'],
            'sn': ['employee_1']
        }
        self.assertEqual(self.conn.get_entry_by_dn(dn).entry_attributes_as_dict, expect)

    def test_set_user_password(self):
        user = self.rdb_executer.create_user(USER_DATA)
        dn = self.ldap_executer.create_user(USER_DATA)
        password = 'password'
        self.ldap_executer.set_user_password(user, password)

        self.assertFalse(self.conn.authenticate(dn, password='wrong password'))
        self.assertTrue(self.conn.authenticate(dn, password))
        self.assertFalse(self.conn.authenticate(dn, ''))

    def test_delete_users(self):
        dn = self.ldap_executer.create_user(USER_DATA)
        self.assertIsNotNone(self.conn.get_entry_by_dn(dn))

        user = self.rdb_executer.create_user(USER_DATA)
        self.ldap_executer.delete_users([user])
        self.assertIsNone(self.conn.get_entry_by_dn(dn))

    def test_create_dept(self):
        dn = self.ldap_executer.create_dept(DEPT_DATA)
        expect = {
            'member': [''],
            'description': ['开发'],
            'cn': ['dev'],
            'objectClass': ['groupOfNames'],
        }
        self.assertEqual(self.conn.get_entry_by_dn(dn).entry_attributes_as_dict, expect)

    def test_update_dept(self):
        dn = self.ldap_executer.create_dept(DEPT_DATA)
        dept = self.rdb_executer.create_dept(DEPT_DATA)
        self.ldap_executer.update_dept(dept, {'description': '新'})
        expect = {
            'member': [''],
            'description': ['新'],
            'cn': ['dev'],
            'objectClass': ['groupOfNames'],
        }
        self.assertEqual(self.conn.get_entry_by_dn(dn).entry_attributes_as_dict, expect)

    def test_delete_dept(self):
        dept = self.rdb_executer.create_dept(DEPT_DATA)
        dn = self.ldap_executer.create_dept(DEPT_DATA)
        self.assertIsNotNone(self.conn.get_entry_by_dn(dn))

        self.ldap_executer.delete_dept(dept)
        self.assertIsNone(self.conn.get_entry_by_dn(dn))

    def test_delete_dept_with_dept(self):
        dept = self.rdb_executer.create_dept(DEPT_DATA)
        parent_dept = self.rdb_executer.create_dept(PARENT_DEPT_DATA)
        self.ldap_executer.create_dept(DEPT_DATA)
        self.ldap_executer.create_dept(PARENT_DEPT_DATA)
        self.rdb_executer.add_dept_to_dept(dept, parent_dept)
        self.ldap_executer.add_dept_to_dept(dept, parent_dept)

        with self.assertRaises(LDAPNotAllowedOnNotLeafResult):
            self.ldap_executer.delete_dept(parent_dept)

    def test_delete_dept_with_member(self):
        dept = self.rdb_executer.create_dept(DEPT_DATA)
        self.ldap_executer.create_dept(DEPT_DATA)

        user = self.rdb_executer.create_user(USER_DATA)
        self.ldap_executer.create_user(USER_DATA)

        self.ldap_executer.add_users_to_dept([user], dept)

        with self.assertRaises(LDAPNotAllowedOnNotLeafResult):
            self.ldap_executer.delete_dept(dept)

    def test_add_dept_to_dept(self):
        dept = self.rdb_executer.create_dept(DEPT_DATA)
        dn = self.ldap_executer.create_dept(DEPT_DATA)

        parent_dept = self.rdb_executer.create_dept(PARENT_DEPT_DATA)
        self.ldap_executer.create_dept(PARENT_DEPT_DATA)

        new_dn = self.ldap_executer.add_dept_to_dept(dept, parent_dept)
        self.assertEqual(new_dn, 'cn=dev,cn=IT,ou=dept,dc=example,dc=org')
        self.assertIsNone(self.conn.get_entry_by_dn(dn))
        self.assertIsNotNone(self.conn.get_entry_by_dn(new_dn))

        self.conn.search('cn=IT,ou=dept,dc=example,dc=org', '(objectClass=groupOfNames)')
        self.assertIn(self.conn.get_entry_by_dn(new_dn), self.conn.entries)

    def test_update_group(self):
        dn = self.ldap_executer.create_group(GROUP_DATA)
        group = self.rdb_executer.create_group(GROUP_DATA)
        self.ldap_executer.update_group(group, {'description': '新'})
        expect = {
            'member': [''],
            'description': ['新'],
            'cn': ['supervisor'],
            'objectClass': ['groupOfNames'],
        }
        self.assertEqual(self.conn.get_entry_by_dn(dn).entry_attributes_as_dict, expect)

    def test_dept_member(self):
        user = self.rdb_executer.create_user(USER_DATA)
        dept = self.rdb_executer.create_dept(DEPT_DATA)
        parent_dept = self.rdb_executer.create_dept(PARENT_DEPT_DATA)

        user_dn = self.ldap_executer.create_user(USER_DATA)
        dept_dn = self.ldap_executer.create_dept(DEPT_DATA)
        parent_dn = self.ldap_executer.create_dept(PARENT_DEPT_DATA)

        self.rdb_executer.add_dept_to_dept(dept, parent_dept)
        dept_dn = self.ldap_executer.add_dept_to_dept(dept, parent_dept)

        # test add users to dept
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(dept_dn).entry_attributes_as_dict['member'])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])

        self.ldap_executer.add_users_to_dept([user], dept)

        self.assertIn(user_dn, self.conn.get_entry_by_dn(dept_dn).entry_attributes_as_dict['member'])
        self.assertEqual(self.conn.get_depts(user.dn), ['cn=dev,cn=IT,ou=dept,dc=example,dc=org'])

        # test delete users from dept
        self.ldap_executer.delete_users_from_dept([user], dept)
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(dept_dn).entry_attributes_as_dict['member'])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])

        # test add user to depts
        self.ldap_executer.add_user_to_depts(user, [dept, parent_dept])
        self.assertIn(user_dn, self.conn.get_entry_by_dn(dept_dn).entry_attributes_as_dict['member'])
        self.assertIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])
        self.assertEqual(
            self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'].count(user_dn),
            1,
        )

        # test delete user from depts
        self.ldap_executer.delete_user_from_depts(user, [dept, parent_dept])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(dept_dn).entry_attributes_as_dict['member'])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])

        # test sort depts in dept
        self.ldap_executer.sort_depts_in_dept([dept], parent_dept)

    def test_delete_group(self):
        group = self.rdb_executer.create_group(GROUP_DATA)
        dn = self.ldap_executer.create_group(GROUP_DATA)
        self.assertIsNotNone(self.conn.get_entry_by_dn(dn))

        self.ldap_executer.delete_group(group)
        self.assertIsNone(self.conn.get_entry_by_dn(dn))

    def test_delete_group_with_group(self):
        group = self.rdb_executer.create_group(GROUP_DATA)
        parent_group = self.rdb_executer.create_group(PARENT_GROUP_DATA)
        self.ldap_executer.create_group(GROUP_DATA)
        self.ldap_executer.create_group(PARENT_GROUP_DATA)
        self.rdb_executer.add_group_to_group(group, parent_group)
        self.ldap_executer.add_group_to_group(group, parent_group)

        with self.assertRaises(LDAPNotAllowedOnNotLeafResult):
            self.ldap_executer.delete_group(parent_group)

    def test_delete_group_with_member(self):
        group = self.rdb_executer.create_group(GROUP_DATA)
        self.ldap_executer.create_group(GROUP_DATA)

        user = self.rdb_executer.create_user(USER_DATA)
        self.ldap_executer.create_user(USER_DATA)

        self.ldap_executer.add_users_to_group([user], group)

        with self.assertRaises(LDAPNotAllowedOnNotLeafResult):
            self.ldap_executer.delete_group(group)

    def test_group_member(self):
        user = self.rdb_executer.create_user(USER_DATA)
        group = self.rdb_executer.create_group(GROUP_DATA)
        parent_group = self.rdb_executer.create_group(PARENT_GROUP_DATA)

        user_dn = self.ldap_executer.create_user(USER_DATA)
        group_dn = self.ldap_executer.create_group(GROUP_DATA)
        parent_dn = self.ldap_executer.create_group(PARENT_GROUP_DATA)

        self.rdb_executer.add_group_to_group(group, parent_group)
        group_dn = self.ldap_executer.add_group_to_group(group, parent_group)

        # test add users to group
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(group_dn).entry_attributes_as_dict['member'])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])

        self.ldap_executer.add_users_to_group([user], group)

        self.assertIn(user_dn, self.conn.get_entry_by_dn(group_dn).entry_attributes_as_dict['member'])
        self.assertEqual(self.conn.get_groups(user.dn), ['cn=supervisor,cn=manager,ou=group,dc=example,dc=org'])

        # test delete users form group
        self.ldap_executer.delete_users_from_group([user], group)
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(group_dn).entry_attributes_as_dict['member'])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])

        # test add user to groups
        self.ldap_executer.add_user_to_groups(user, [group, parent_group])
        self.assertIn(user_dn, self.conn.get_entry_by_dn(group_dn).entry_attributes_as_dict['member'])
        self.assertIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])
        self.assertEqual(
            self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'].count(user_dn),
            1,
        )

        # test delete user from groups
        self.ldap_executer.delete_user_from_groups(user, [group, parent_group])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(group_dn).entry_attributes_as_dict['member'])
        self.assertNotIn(user_dn, self.conn.get_entry_by_dn(parent_dn).entry_attributes_as_dict['member'])

        # test sort groups in group
        self.ldap_executer.sort_groups_in_group([group], parent_group)


class LDAPExecuterDeptTestCase(LDAPBaseTestCase):
    def setUp(self):
        '''
        dept
        |
        IT ---\
        |      \
        dev    tmp
        |  \
        fe  be
        '''
        super(LDAPExecuterDeptTestCase, self).setUp()

        self.user = self.cli.create_user(USER_DATA)

        self.parent_dept = self.cli.create_dept(PARENT_DEPT_DATA)
        self.cli.add_dept_to_dept(self.parent_dept, Dept.valid_objects.get(uid='root'))

        self.dept_1 = self.cli.create_dept(DEPT_DATA)
        self.cli.add_dept_to_dept(self.dept_1, self.parent_dept)

        self.dept_2 = self.cli.create_dept(DEPT_2_DATA)
        self.cli.add_dept_to_dept(self.dept_2, self.parent_dept)

        self.child_dept_1 = self.cli.create_dept(CHILD_DEPT_1_DATA)
        self.cli.add_dept_to_dept(self.child_dept_1, self.dept_1)

        self.child_dept_2 = self.cli.create_dept(CHILD_DEPT_2_DATA)
        self.cli.add_dept_to_dept(self.child_dept_2, self.dept_1)

        # user -> fe
        self.cli.add_users_to_dept([self.user], self.child_dept_1)

        # user -> tmp
        self.cli.add_users_to_dept([self.user], self.dept_2)

    def test_delete_user(self):
        self.assertIn(self.user.dn, self.conn.get_members(self.dept_2.dn))
        self.cli.delete_users([self.user])
        self.assertNotIn(self.user.dn, self.conn.get_members(self.dept_2.dn))

    def test_add_multiple_dept(self):
        self.cli.add_users_to_dept([self.user], self.dept_1)
        self.cli.add_users_to_dept([self.user], self.dept_2)

    def test_dept_circle_lock(self):
        with self.assertRaises(LDAPUnwillingToPerformResult):
            self.ldap_executer.move_dept_to_dept(self.dept_1, self.child_dept_1)

    def test_move_dept_to_dept(self):

        # dev -> tmp
        dn = self.ldap_executer.move_dept_to_dept(self.dept_1, self.dept_2)
        self.assertEqual(dn, 'cn=dev,cn=tmp,cn=IT,ou=dept,dc=example,dc=org')

        # 父部门修改dn后，子部门自动随之修改dn
        self.conn.search(self.ldap_executer.dept_base, '(cn=be)')
        self.assertEqual(self.conn.entries[0].entry_dn, 'cn=be,cn=dev,cn=tmp,cn=IT,ou=dept,dc=example,dc=org')
        self.conn.search(self.ldap_executer.dept_base, '(cn=fe)')
        self.assertEqual(self.conn.entries[0].entry_dn, 'cn=fe,cn=dev,cn=tmp,cn=IT,ou=dept,dc=example,dc=org')

        self.assertIn(self.user.dn, self.conn.get_members('cn=fe,cn=dev,cn=tmp,cn=IT,ou=dept,dc=example,dc=org'))
        self.assertIn(self.user.dn, self.conn.get_members('cn=tmp,cn=IT,ou=dept,dc=example,dc=org'))
        self.assertIsNone(self.conn.get_entry_by_dn('cn=dev,cn=IT,ou=dept,dc=example,dc=org'))
        self.assertIsNone(self.conn.get_entry_by_dn('cn=fe,cn=dev,cn=IT,ou=dept,dc=example,dc=org'))

        # 子部门自动修改后，memberOf随之自动修改
        self.assertEqual(self.conn.get_depts(self.user.dn), [
            'cn=tmp,cn=IT,ou=dept,dc=example,dc=org',
            'cn=fe,cn=dev,cn=tmp,cn=IT,ou=dept,dc=example,dc=org',
        ])


class LDAPExecuterGroupTestCase(LDAPBaseTestCase):
    def setUp(self):
        super(LDAPExecuterGroupTestCase, self).setUp()

        self.user = self.cli.create_user(USER_DATA)

        self.parent_group = self.cli.create_group(PARENT_DEPT_DATA)
        self.cli.add_group_to_group(self.parent_group, Group.valid_objects.get(uid='root'))

        self.group_1 = self.cli.create_group(DEPT_DATA)
        self.cli.add_group_to_group(self.group_1, self.parent_group)

        self.group_2 = self.cli.create_group(DEPT_2_DATA)
        self.cli.add_group_to_group(self.group_2, self.parent_group)

        self.child_group_1 = self.cli.create_group(CHILD_DEPT_1_DATA)
        self.cli.add_group_to_group(self.child_group_1, self.group_1)

        self.child_group_2 = self.cli.create_group(CHILD_DEPT_2_DATA)
        self.cli.add_group_to_group(self.child_group_2, self.group_1)

        # user -> fe
        self.cli.add_users_to_group([self.user], self.child_group_1)

        # user -> tmp
        self.cli.add_users_to_group([self.user], self.group_2)

    def test_add_multiple_group(self):
        self.cli.add_users_to_group([self.user], self.group_1)
        self.cli.add_users_to_group([self.user], self.group_2)

    def test_delete_users(self):
        self.assertIn(self.user.dn, self.conn.get_members(self.group_2.dn))
        self.cli.delete_users([self.user])
        self.assertNotIn(self.user.dn, self.conn.get_members(self.group_2.dn))

    def test_group_circle_lock(self):
        with self.assertRaises(LDAPUnwillingToPerformResult):
            self.ldap_executer.move_group_to_group(self.group_1, self.child_group_1)

    def test_move_group_to_group(self):

        # dev -> tmp
        dn = self.ldap_executer.move_group_to_group(self.group_1, self.group_2)
        self.assertEqual(dn, 'cn=dev,cn=tmp,cn=IT,ou=group,dc=example,dc=org')

        # 父部门修改dn后，子部门自动随之修改dn
        self.conn.search(self.ldap_executer.group_base, '(cn=be)')
        self.assertEqual(self.conn.entries[0].entry_dn, 'cn=be,cn=dev,cn=tmp,cn=IT,ou=group,dc=example,dc=org')
        self.conn.search(self.ldap_executer.group_base, '(cn=fe)')
        self.assertEqual(self.conn.entries[0].entry_dn, 'cn=fe,cn=dev,cn=tmp,cn=IT,ou=group,dc=example,dc=org')

        self.assertIn(self.user.dn, self.conn.get_members('cn=fe,cn=dev,cn=tmp,cn=IT,ou=group,dc=example,dc=org'))
        self.assertIn(self.user.dn, self.conn.get_members('cn=tmp,cn=IT,ou=group,dc=example,dc=org'))
        self.assertIsNone(self.conn.get_entry_by_dn('cn=dev,cn=IT,ou=group,dc=example,dc=org'))
        self.assertIsNone(self.conn.get_entry_by_dn('cn=fe,cn=dev,cn=IT,ou=group,dc=example,dc=org'))

        # 子部门自动修改后，memberOf随之自动修改
        self.assertEqual(self.conn.get_groups(self.user.dn), [
            'cn=tmp,cn=IT,ou=group,dc=example,dc=org',
            'cn=fe,cn=dev,cn=tmp,cn=IT,ou=group,dc=example,dc=org',
        ])
