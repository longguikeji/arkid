"""
tests for api about ucenter tree
"""

# pylint: disable=missing-docstring, too-many-lines

from django.urls import reverse
from siteapi.v1.tests import TestCase
from siteapi.v1.tests.test_node import create_node_tree
from oneid_meta.models import Dept, Group, User, GroupMember, DeptMember

TREE = {
    '1': {
        '1-1': {
            '1-1-1': {
                '1-1-1-1': {},
            },
            '1-1-2': {},
        },
        '1-2': {
            '1-2-1': {},
            '1-2-2': {},
        },
        '1-3': {
            '1-3-1': {},
            '1-3-2': {},
            '1-3-3': {},
        }
    }
}


class VisibleTreeTestCase(TestCase):
    def setUp(self):
        list(create_node_tree(Dept, TREE))
        list(create_node_tree(Group, TREE))

        self.user = User.objects.create(username='test')
        for node in Group.valid_objects.all():
            GroupMember.objects.create(owner=node, user=self.user)
        for node in Dept.valid_objects.all():
            DeptMember.objects.create(owner=node, user=self.user)

        reject_uids = ['1-1', '1-1-1', '1-2', '1-2-1', '1-2-2', '1-3-1']
        for node in Group.valid_objects.filter(uid__in=reject_uids):
            node.visibility = 5
            node.save()
        for node in Dept.valid_objects.filter(uid__in=reject_uids):
            node.visibility = 5
            node.save()

        self.client = self.login_as(self.user)

    def test_get_visible_dept(self):
        res = self.client.get(reverse('siteapi:ucenter_node_tree', args=('d_1', )))
        expect = {
            'info': {
                'dept_id': 2,
                'node_uid': 'd_1',
                'node_subject': 'dept',
                'uid': '1',
                'name': '1',
                'remark': ''
            },
            'nodes': [{
                'info': {
                    'dept_id': 3,
                    'node_uid': 'd_1-1',
                    'node_subject': 'dept',
                    'uid': '1-1',
                    'name': '1-1'
                },
                'nodes': [{
                    'info': {
                        'dept_id': 4,
                        'node_uid': 'd_1-1-1',
                        'node_subject': 'dept',
                        'uid': '1-1-1',
                        'name': '1-1-1'
                    },
                    'nodes': [{
                        'info': {
                            'dept_id': 5,
                            'node_uid': 'd_1-1-1-1',
                            'node_subject': 'dept',
                            'uid': '1-1-1-1',
                            'name': '1-1-1-1',
                            'remark': ''
                        },
                        'nodes': []
                    }]
                }, {
                    'info': {
                        'dept_id': 6,
                        'node_uid': 'd_1-1-2',
                        'node_subject': 'dept',
                        'uid': '1-1-2',
                        'name': '1-1-2',
                        'remark': ''
                    },
                    'nodes': []
                }]
            }, {
                'info': {
                    'dept_id': 10,
                    'node_uid': 'd_1-3',
                    'node_subject': 'dept',
                    'uid': '1-3',
                    'name': '1-3',
                    'remark': ''
                },
                'nodes': [{
                    'info': {
                        'dept_id': 12,
                        'node_uid': 'd_1-3-2',
                        'node_subject': 'dept',
                        'uid': '1-3-2',
                        'name': '1-3-2',
                        'remark': ''
                    },
                    'nodes': []
                }, {
                    'info': {
                        'dept_id': 13,
                        'node_uid': 'd_1-3-3',
                        'node_subject': 'dept',
                        'uid': '1-3-3',
                        'name': '1-3-3',
                        'remark': ''
                    },
                    'nodes': []
                }]
            }]
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:ucenter_node_tree', args=('d_1', )), data={'user_required': True})
        expect = {
            'info': {
                'dept_id': 2,
                'node_uid': 'd_1',
                'node_subject': 'dept',
                'uid': '1',
                'name': '1',
                'remark': ''
            },
            'users': [{
                'user_id': 2,
                'username': 'test',
                'name': ''
            }],
            'nodes': [{
                'info': {
                    'dept_id': 3,
                    'node_uid': 'd_1-1',
                    'node_subject': 'dept',
                    'uid': '1-1',
                    'name': '1-1'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 4,
                        'node_uid': 'd_1-1-1',
                        'node_subject': 'dept',
                        'uid': '1-1-1',
                        'name': '1-1-1'
                    },
                    'users': [],
                    'nodes': [{
                        'info': {
                            'dept_id': 5,
                            'node_uid': 'd_1-1-1-1',
                            'node_subject': 'dept',
                            'uid': '1-1-1-1',
                            'name': '1-1-1-1',
                            'remark': ''
                        },
                        'users': [{
                            'user_id': 2,
                            'username': 'test',
                            'name': ''
                        }],
                        'nodes': [],
                        'headcount': 1
                    }],
                    'headcount':
                    1
                }, {
                    'info': {
                        'dept_id': 6,
                        'node_uid': 'd_1-1-2',
                        'node_subject': 'dept',
                        'uid': '1-1-2',
                        'name': '1-1-2',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 2,
                        'username': 'test',
                        'name': ''
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 10,
                    'node_uid': 'd_1-3',
                    'node_subject': 'dept',
                    'uid': '1-3',
                    'name': '1-3',
                    'remark': ''
                },
                'users': [{
                    'user_id': 2,
                    'username': 'test',
                    'name': ''
                }],
                'nodes': [{
                    'info': {
                        'dept_id': 12,
                        'node_uid': 'd_1-3-2',
                        'node_subject': 'dept',
                        'uid': '1-3-2',
                        'name': '1-3-2',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 2,
                        'username': 'test',
                        'name': ''
                    }],
                    'nodes': [],
                    'headcount': 1
                }, {
                    'info': {
                        'dept_id': 13,
                        'node_uid': 'd_1-3-3',
                        'node_subject': 'dept',
                        'uid': '1-3-3',
                        'name': '1-3-3',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 2,
                        'username': 'test',
                        'name': ''
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }],
            'headcount':
            1
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:ucenter_node_tree', args=('d_1-2-1', )))
        self.assertEqual(res.status_code, 404)

    def test_get_visible_group(self):
        res = self.client.get(reverse('siteapi:ucenter_node_tree', args=('g_1', )))
        expect = {
            'info': {
                'group_id': 2,
                'node_uid': 'g_1',
                'node_subject': 'root',
                'uid': '1',
                'name': '1',
                'remark': '',
                'accept_user': True
            },
            'nodes': [{
                'info': {
                    'group_id': 3,
                    'node_uid': 'g_1-1',
                    'node_subject': 'root',
                    'uid': '1-1',
                    'name': '1-1'
                },
                'nodes': [{
                    'info': {
                        'group_id': 4,
                        'node_uid': 'g_1-1-1',
                        'node_subject': 'root',
                        'uid': '1-1-1',
                        'name': '1-1-1'
                    },
                    'nodes': [{
                        'info': {
                            'group_id': 5,
                            'node_uid': 'g_1-1-1-1',
                            'node_subject': 'root',
                            'uid': '1-1-1-1',
                            'name': '1-1-1-1',
                            'remark': '',
                            'accept_user': True
                        },
                        'nodes': []
                    }]
                }, {
                    'info': {
                        'group_id': 6,
                        'node_uid': 'g_1-1-2',
                        'node_subject': 'root',
                        'uid': '1-1-2',
                        'name': '1-1-2',
                        'remark': '',
                        'accept_user': True
                    },
                    'nodes': []
                }]
            }, {
                'info': {
                    'group_id': 10,
                    'node_uid': 'g_1-3',
                    'node_subject': 'root',
                    'uid': '1-3',
                    'name': '1-3',
                    'remark': '',
                    'accept_user': True
                },
                'nodes': [{
                    'info': {
                        'group_id': 12,
                        'node_uid': 'g_1-3-2',
                        'node_subject': 'root',
                        'uid': '1-3-2',
                        'name': '1-3-2',
                        'remark': '',
                        'accept_user': True
                    },
                    'nodes': []
                }, {
                    'info': {
                        'group_id': 13,
                        'node_uid': 'g_1-3-3',
                        'node_subject': 'root',
                        'uid': '1-3-3',
                        'name': '1-3-3',
                        'remark': '',
                        'accept_user': True
                    },
                    'nodes': []
                }]
            }]
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:ucenter_node_tree', args=('g_1', )), data={'user_required': True})
        expect = {
            'info': {
                'group_id': 2,
                'node_uid': 'g_1',
                'node_subject': 'root',
                'uid': '1',
                'name': '1',
                'remark': '',
                'accept_user': True
            },
            'users': [{
                'user_id': 2,
                'username': 'test',
                'name': ''
            }],
            'nodes': [{
                'info': {
                    'group_id': 3,
                    'node_uid': 'g_1-1',
                    'node_subject': 'root',
                    'uid': '1-1',
                    'name': '1-1'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'group_id': 4,
                        'node_uid': 'g_1-1-1',
                        'node_subject': 'root',
                        'uid': '1-1-1',
                        'name': '1-1-1'
                    },
                    'users': [],
                    'nodes': [{
                        'info': {
                            'group_id': 5,
                            'node_uid': 'g_1-1-1-1',
                            'node_subject': 'root',
                            'uid': '1-1-1-1',
                            'name': '1-1-1-1',
                            'remark': '',
                            'accept_user': True
                        },
                        'users': [{
                            'user_id': 2,
                            'username': 'test',
                            'name': ''
                        }],
                        'nodes': [],
                        'headcount': 1
                    }],
                    'headcount':
                    1
                }, {
                    'info': {
                        'group_id': 6,
                        'node_uid': 'g_1-1-2',
                        'node_subject': 'root',
                        'uid': '1-1-2',
                        'name': '1-1-2',
                        'remark': '',
                        'accept_user': True
                    },
                    'users': [{
                        'user_id': 2,
                        'username': 'test',
                        'name': ''
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'group_id': 10,
                    'node_uid': 'g_1-3',
                    'node_subject': 'root',
                    'uid': '1-3',
                    'name': '1-3',
                    'remark': '',
                    'accept_user': True
                },
                'users': [{
                    'user_id': 2,
                    'username': 'test',
                    'name': ''
                }],
                'nodes': [{
                    'info': {
                        'group_id': 12,
                        'node_uid': 'g_1-3-2',
                        'node_subject': 'root',
                        'uid': '1-3-2',
                        'name': '1-3-2',
                        'remark': '',
                        'accept_user': True
                    },
                    'users': [{
                        'user_id': 2,
                        'username': 'test',
                        'name': ''
                    }],
                    'nodes': [],
                    'headcount': 1
                }, {
                    'info': {
                        'group_id': 13,
                        'node_uid': 'g_1-3-3',
                        'node_subject': 'root',
                        'uid': '1-3-3',
                        'name': '1-3-3',
                        'remark': '',
                        'accept_user': True
                    },
                    'users': [{
                        'user_id': 2,
                        'username': 'test',
                        'name': ''
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }],
            'headcount':
            1
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:ucenter_node_tree', args=('d_1-2-1', )))
        self.assertEqual(res.status_code, 404)


class NodeVisibleTestCase(TestCase):
    def setUp(self):
        list(create_node_tree(Dept, TREE))

        self.user = User.objects.create(username='test')
        # for node in Dept.valid_objects.all():
        #     DeptMember.objects.create(owner=node, user=self.user)

    def test_dept_visible_1(self):
        node = Dept.valid_objects.get(uid='1')
        node.visibility = 1
        node.save()
        self.assertTrue(node.is_open_to_employee(self.user))

    def test_dept_visible_5(self):
        node = Dept.valid_objects.get(uid='1')
        node.visibility = 5
        node.save()
        self.assertFalse(node.is_open_to_employee(self.user))

    def test_dept_visible_2(self):
        node = Dept.valid_objects.get(uid='1')
        node.visibility = 2
        node.save()

        self.assertFalse(node.is_open_to_employee(self.user))

        node.member_cls.objects.create(owner=Dept.valid_objects.get(uid='1-1'), user=self.user)
        self.assertFalse(node.is_open_to_employee(self.user))

        node.member_cls.objects.create(owner=node, user=self.user)
        self.assertTrue(node.is_open_to_employee(self.user))

    def test_dept_visible_3(self):
        node = Dept.valid_objects.get(uid='1')
        node.visibility = 3
        node.save()

        self.assertFalse(node.is_open_to_employee(self.user))

        node.member_cls.objects.create(owner=Dept.valid_objects.get(uid='1-1'), user=self.user)
        self.assertTrue(node.is_open_to_employee(self.user))

    def test_dept_visible_4(self):
        node = Dept.valid_objects.get(uid='1')
        node.visibility = 4
        node.save()

        self.assertFalse(node.is_open_to_employee(self.user))

        node.user_scope = ['test']
        node.save()
        self.assertTrue(node.is_open_to_employee(self.user))

        node.user_scope = []
        node.save()
        self.assertFalse(node.is_open_to_employee(self.user))

        node.node_scope = ['d_1-1']
        node.save()
        self.assertFalse(node.is_open_to_employee(self.user))

        node.member_cls.objects.create(owner=node.__class__.objects.get(uid='1-2'), user=self.user)
        self.assertFalse(node.is_open_to_employee(self.user))

        node.member_cls.objects.create(owner=node.__class__.objects.get(uid='1-1-1'), user=self.user)
        self.assertTrue(node.is_open_to_employee(self.user))
