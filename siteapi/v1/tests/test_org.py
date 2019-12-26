'''
tests for api abort org
'''

# pylint: disable=missing-docstring, invalid-name, too-many-locals

from uuid import uuid4
from django.urls import reverse
from oneid_meta.models import User, Dept, Group, GroupMember, Org

from siteapi.v1.tests import TestCase
from siteapi.v1.serializers.org import OrgSerializer

ORG_DATA = [
    {
        'name': '组织1'
    },
    {
        'name': '组织2'
    },
]

ILL_FORMED_DATA = {'name2': '组织3'}


class OrgTestCase(TestCase):
    def setUp(self):
        super(OrgTestCase, self).setUp()
        self._client = self.client

        for org in ORG_DATA:
            for o in Org.valid_objects.filter(name=org['name']):
                o.kill()

    def tearDown(self):
        super(OrgTestCase, self).tearDown()
        for org in ORG_DATA:
            for o in Org.valid_objects.filter(name=org['name']):
                o.kill()

    def set_client(self, client):
        self.client = client

    def unset_client(self):
        self.client = self._client

    def list_org(self):
        return self.client.get(reverse('siteapi:org_create'))

    def create_org(self, org_data):
        return self.client.json_post(reverse('siteapi:org_create'), data=org_data)

    def delete_org(self, org_oid):
        return self.client.delete(reverse('siteapi:org_detail', args=(org_oid, )))

    def inspect_org(self, org_oid):
        return self.client.get(reverse('siteapi:org_detail', args=(org_oid, )))

    def create_dept(self, uid, name):
        return self.client.json_post(reverse('siteapi:dept_child_dept', args=(uid, )), data={'name': name})

    def create_group(self, uid, name):
        return self.client.json_post(reverse('siteapi:group_child_group', args=(uid, )), data={'name': name})

    def get_org(self):
        return self.client.get(reverse('siteapi:ucenter_org_list'))

    def get_owned_org(self):
        return self.client.get(reverse('siteapi:ucenter_own_org_list'))

    def get_curr_org(self):
        return self.client.get(reverse('siteapi:ucenter_org'))

    def set_curr_org(self, data):
        return self.client.json_post(reverse('siteapi:ucenter_org'), data=data)

    def clear_curr_org(self):
        return self.client.delete(reverse('siteapi:ucenter_org'))

    def create_user(self, grp_uids, dept_uids, name):
        return self.client.json_post(reverse('siteapi:user_list'),
                                     data={
                                         'group_uids': grp_uids,
                                         'dept_uids': dept_uids,
                                         'user': {
                                             'username': name
                                         }
                                     })

    def get_user(self, org_oid):
        return self.client.get(reverse('siteapi:org_user', args=(org_oid, )))

    def test_org_management(self):
        orgs = []
        owner = User.create_user('owner', 'owner')
        other = User.create_user('other', 'other')

        for org in ORG_DATA:
            orgs.append((org, self.create_org(org)))

        self.assertEqual(self.create_org(ILL_FORMED_DATA).status_code, 400)

        # external
        for (org, res) in orgs:
            self.assertEqual(org['name'], res.json()['name'])
        jorgs = [res.json() for (org, res) in orgs]

        # internal
        iorgs = []
        for (org, res) in orgs:
            o = Org.valid_objects.filter(uuid=Org.to_uuid(res.json()['oid'])).first()    # oid -> name
            self.assertEqual(str(o.uuid), Org.to_uuid(res.json()['oid']))
            self.assertEqual(o.name, res.json()['name'])
            self.assertEqual(o.dept.uid, res.json()['dept_uid'])
            self.assertEqual(o.group.uid, res.json()['group_uid'])
            self.assertEqual(o.direct.uid, res.json()['direct_uid'])
            self.assertEqual(o.manager.uid, res.json()['manager_uid'])
            self.assertEqual(o.role.uid, res.json()['role_uid'])
            self.assertEqual(o.label.uid, res.json()['label_uid'])
            iorgs.append((o, res.json()))

        # external, internal behavior justified by previous assertion && transitivity
        for res in jorgs:
            self.assertEqual(res, self.inspect_org(res['oid']).json())

        self.assertEqual(self.inspect_org('invalid-oid').status_code, 400)
        self.assertEqual(self.inspect_org(uuid4()).status_code, 404)

        # external
        self.assertEqual(jorgs, self.list_org().json())

        # internal
        self.assertEqual(self.list_org().json(), [OrgSerializer(o).data for o in Org.valid_objects.all()])

        # perm
        self.set_client(self.login_as(owner))
        self.assertEqual(self.list_org().status_code, 403)
        self.unset_client()

        def eq_leibniz(x, y, f):
            self.assertEqual(x, y)
            self.assertEqual(f(x), f(y))

        def eq_dept(d1):
            d2 = Dept.valid_objects.filter(uid=d1.uid).first()
            eq_leibniz(d1, d2, lambda x: x.parent)

        def eq_group(g1):
            g2 = Group.valid_objects.filter(uid=g1.uid).first()
            eq_leibniz(g1, g2, lambda x: x.parent)

        # schema validity
        for (o, res) in iorgs:
            eq_dept(o.dept)
            eq_group(o.group)
            eq_group(o.direct)
            eq_group(o.manager)
            eq_group(o.role)
            eq_group(o.label)

        # external
        for res in jorgs:
            self.assertEqual(self.delete_org(res['oid']).status_code, 204)
        self.assertEqual([], self.list_org().json())

        # internal
        self.assertEqual([], [OrgSerializer(o).data for o in Org.valid_objects.all()])
        # soft delete
        self.assertEqual(jorgs, [OrgSerializer(o).data for o in Org.objects.all()])

        # perm
        self.set_client(self.login_as(owner))
        op1 = self.create_org({'name': 'org_perm_1'}).json()['oid']
        op2 = self.create_org({'name': 'org_perm_2'}).json()['oid']
        self.set_client(self.login_as(other))
        self.assertEqual(self.delete_org(op1).status_code, 403)
        self.set_client(self.login_as(owner))
        self.assertEqual(self.delete_org(op1).status_code, 204)
        self.unset_client()
        self.assertEqual(self.delete_org(op2).status_code, 204)

    def test_org_member(self):
        owner = User.create_user('owner', 'owner')
        other = User.create_user('other', 'other')

        self.set_client(self.login_as(owner))
        org = self.create_org({'name': '组织1'}).json()
        self.unset_client()

        dept = org['dept_uid']
        dept_a = self.create_dept(dept, 'Dept A').json()['uid']

        grp = org['group_uid']
        grptype_a = self.create_group(grp, 'Type A').json()['uid']
        grp_a_a = self.create_group(grptype_a, 'Group A').json()['uid']

        direct = org['direct_uid']

        manager = org['manager_uid']

        role = org['role_uid']
        role_a = self.create_group(role, 'Role A').json()['uid']

        role_b = self.create_group(role, 'Role B').json()['uid']
        role_ab = self.create_group(role_a, 'Subrole AB').json()['uid']

        label = org['label_uid']
        label_a = self.create_group(label, 'Label A').json()['uid']

        self.create_user(['root'], [dept_a], 'user0')
        self.create_user(['root', grp_a_a], ['root'], 'user1')
        self.create_user([direct], ['root'], 'user2')
        self.create_user([manager, role_a, grp_a_a], [dept_a], 'user3')
        self.create_user([direct, role_a, role_ab, label_a, manager], ['root'], 'user4')
        self.create_user(['root', label_a, role_b, role_ab, role, grptype_a, grp], [dept, dept_a], 'user5')

        # with owner
        user_data = {'owner', 'user0', 'user1', 'user2', 'user3', 'user4', 'user5'}
        self.assertEqual(set(self.get_user(org['oid']).json()), user_data)

        #perm
        self.set_client(self.login_as(owner))
        self.assertEqual(set(self.get_user(org['oid']).json()), user_data)
        self.set_client(self.login_as(other))
        self.assertEqual(self.get_user(org['oid']).status_code, 403)
        self.unset_client()

    # 节点-添加成员-API

    def test_user_org(self):
        user = User.create_user('user', 'user')
        extern_org = self.create_org({'name': '外部组织'}).json()
        GroupMember.valid_objects.create(user=user,
                                         owner=Group.valid_objects.filter(uid=extern_org['direct_uid']).first())

        self.set_client(self.login_as(user))
        oid = set(map(lambda x: self.create_org(x).json()['oid'], ORG_DATA))
        self.assertEqual(set(map(lambda o: o['oid'], self.get_owned_org().json())), oid)
        self.assertEqual(set(map(lambda o: o['oid'], self.get_org().json())), oid.union({extern_org['oid']}))

        self.assertEqual(self.get_curr_org().content, b'')
        for o in oid:
            self.assertEqual(self.set_curr_org({'oid': o}).status_code, 204)
            self.assertEqual(self.get_curr_org().json()['oid'], o)

        self.assertEqual(self.set_curr_org({'oid': extern_org['oid']}).status_code, 204)
        self.assertEqual(self.get_curr_org().json()['oid'], extern_org['oid'])
        self.assertEqual(self.set_curr_org({'no_oid': 123}).status_code, 400)
        self.assertEqual(self.set_curr_org({'oid': 'invalid-oid'}).status_code, 400)
        self.assertEqual(self.set_curr_org({'oid': str(uuid4())}).status_code, 404)

        self.assertEqual(self.get_curr_org().json()['oid'], extern_org['oid'])
        self.assertEqual(self.clear_curr_org().status_code, 204)
        self.assertEqual(self.get_curr_org().content, b'')
