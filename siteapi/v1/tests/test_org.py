'''
tests for api abort org
'''

from django.urls import reverse
from siteapi.v1.tests import TestCase

from oneid_meta.models.org import Org
from oneid_meta.models import Dept, Group
from siteapi.v1.views.org import org_ser

ORG_DATA = [
    { 'name': '组织1' },
    { 'name': '组织2' },
]

ILL_FORMED_DATA = { 'name2': '组织3' }

class OrgTestCase(TestCase):
    def setUp(self):
        super(OrgTestCase, self).setUp()
        for org in ORG_DATA:
            for o in Org.objects.filter(name=org['name']):
                o.kill()

    def tearDown(self):
        super(OrgTestCase, self).tearDown()
        for org in ORG_DATA:
            for o in Org.objects.filter(name=org['name']):
                o.kill()

    def list_org(self):
        return self.client.get(reverse('siteapi:org_create'))

    def create_org(self, org_data):
        return self.client.json_post(reverse('siteapi:org_create'), data=org_data)

    def delete_org(self, org_oid):
        return self.client.delete(reverse('siteapi:org_detail', args=(org_oid, )))

    def inspect_org(self, org_oid):
        return self.client.get(reverse('siteapi:org_detail', args=(org_oid, )))

    def test_org_management(self):
        orgs = []

        for org in ORG_DATA:
            orgs.append((org, self.create_org(org)))

        # external
        for (org, res) in orgs:
            self.assertEqual(org['name'], res.json()['name'])
        jorgs = [res.json() for (org, res) in orgs]

        # internal
        iorgs = []
        for (org, res) in orgs:
            o = Org.valid_objects.filter(uuid=Org.to_uuid(res.json()['oid'])).first() # oid -> name
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
        self.assertEqual(self.inspect_org('25518eea-f1ec-4cff-8f68-0cf58bb09962').status_code, 404)

        # external
        self.assertEqual(jorgs, self.list_org().json())

        # internal
        self.assertEqual(self.list_org().json(), [org_ser(o) for o in Org.valid_objects.all()])


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
            self.delete_org(res['oid'])
        self.assertEqual([], self.list_org().json())

        # internal
        self.assertEqual([], [org_ser(o) for o in Org.valid_objects.all()])
        # soft delete
        self.assertEqual(jorgs, [org_ser(o) for o in Org.objects.all()])
