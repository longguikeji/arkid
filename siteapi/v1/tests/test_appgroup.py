"""
tests for api about app group
"""
from django.urls import reverse

from oneid_meta.models import Org, User, AppGroup
from siteapi.v1.tests import TestCase

APP_GROUP = {'name': 'app-group', 'remark': '', 'uid': 'app-group'}

APP_GROUP_1 = {'name': 'app-group-1', 'remark': '', 'uid': 'app-group-1'}

APP_GROUP_2 = {'name': 'app-group-2', 'remark': '', 'uid': 'app-group-2'}


class AppGroupTestCase(TestCase):
    """
    应用分组管理测试
    """
    mock_now = True

    def setUp(self):
        super(AppGroupTestCase, self).setUp()
        # 删去默认建立的组织
        default_org = Org.objects.first()
        if default_org:
            default_org.delete()
        user = User.create_user(username='u1', password='u1')    # 初始化普通用户u1
        self.org = Org.create(name='org', owner=user)    # 已u1的身份初始化一个组织
        self.client = self.login_as(user)    # 已u1的身份登录

    def test_create_child_appgroup(self):
        """测试创建子应用分组"""
        # 组织拥有者创建分组
        res = self.client.json_post(reverse('siteapi:appgroup_child_appgroup', args=(self.org.app_group.uid, )),
                                    data=APP_GROUP)
        expect = {
            'parent_uid': str(self.org.app_group.uid),
            'parent_node_uid': self.org.app_group.node_uid,
            'parent_name': self.org.app_group.name,
            'uid': 'app-group',
            'node_uid': 'ag_app-group',
            'name': 'app-group',
            'remark': '',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(expect, res.json())

    def test_get_child_appgroup(self):
        """测试获取子应用分组列表信息"""
        # 组织拥有者获取分组
        res = self.client.get(reverse('siteapi:appgroup_child_appgroup', args=(self.org.app_group.uid, )))
        print('res is', res.json())
        expect = {
            'node_uid': self.org.default_app_group.node_uid,
            'uid': self.org.default_app_group.uid,
            'name': 'org-默认应用',
            'remark': ''
        }
        self.assertEqual(expect, res.json()['app_groups'].pop())

    def test_adjust_child_appgroup(self):
        """测试调整子应用分组"""
        # 在默认应用分组下，创建两个子应用分组(组织拥有者的身份)
        AppGroup.valid_objects.create()
        appgroup_1 = self.client.json_post(reverse('siteapi:appgroup_child_appgroup',
                                                   args=(self.org.default_app_group.uid, )),
                                           data=APP_GROUP_1).json()
        appgroup_2 = self.client.json_post(reverse('siteapi:appgroup_child_appgroup',
                                                   args=(self.org.default_app_group.uid, )),
                                           data=APP_GROUP_2).json()
        res = self.client.get(reverse('siteapi:appgroup_child_appgroup', args=(self.org.default_app_group.uid, )))
        expect = [{
            'node_uid': 'ag_app-group-1',
            'uid': 'app-group-1',
            'name': 'app-group-1',
            'remark': ''
        }, {
            'node_uid': 'ag_app-group-2',
            'uid': 'app-group-2',
            'name': 'app-group-2',
            'remark': ''
        }]
        self.assertEqual(expect, res.json()['app_groups'])
        # 组织拥有者调整子应用分组
        #   1) 排序子应用分组
        res = self.client.json_patch(reverse('siteapi:appgroup_child_appgroup',
                                             args=(self.org.default_app_group.uid, )),
                                     data={
                                         'app_group_uids': [appgroup_2['uid'], appgroup_1['uid']],
                                         'subject': 'sort'
                                     })
        expect.reverse()
        self.assertEqual(expect, res.json()['app_groups'])
        #   2) 添加子应用分组
        # 将 appgroup_2 分组添加到 appgroup_1 的分组下
        res = self.client.json_patch(reverse('siteapi:appgroup_child_appgroup', args=(appgroup_1['uid'], )),
                                     data={
                                         'app_group_uids': [appgroup_2['uid']],
                                         'subject': 'add'
                                     })
        expect = [{'node_uid': 'ag_app-group-2', 'uid': 'app-group-2', 'name': 'app-group-2', 'remark': ''}]
        self.assertEqual(expect, res.json()['app_groups'])

    def test_get_appgroup(self):
        """测试获取应用分组的信息"""
        # 组织拥有者获取应用分组信息
        res = self.client.get(reverse('siteapi:appgroup_detail', args=(self.org.app_group.uid, )))
        expect = {
            'parent_uid': 'root',
            'parent_node_uid': 'ag_root',
            'parent_name': 'root',
            'uid': self.org.app_group.uid,
            'node_uid': self.org.app_group.node_uid,
            'name': 'org-应用',
            'remark': '',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(expect, res.json())

    def test_update_appgroup(self):
        """测试修改应用分组的信息"""
        # 组织拥有者修改应用分组信息
        res = self.client.json_patch(reverse('siteapi:appgroup_detail', args=(self.org.app_group.uid, )),
                                     data={
                                         'remark': 'test',
                                         'name': 'test'
                                     })
        expect = {
            'parent_uid': 'root',
            'parent_node_uid': 'ag_root',
            'parent_name': 'root',
            'uid': self.org.app_group.uid,
            'node_uid': self.org.app_group.node_uid,
            'name': 'test',
            'remark': 'test',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(expect, res.json())

    def test_delete_appgroup(self):
        """测试删除应用分组"""
        # 组织拥有者删除有子节点的应用分组
        res = self.client.delete(reverse('siteapi:appgroup_detail', args=(self.org.app_group.uid, )))
        self.assertEqual(400, res.status_code)

        # 组织拥有者删除无子节点的应用分组
        res = self.client.delete(reverse('siteapi:appgroup_detail', args=(self.org.default_app_group.uid, )))
        self.assertEqual(204, res.status_code)

    def test_get_appgroup_tree(self):
        """测试获取完整应用分组结构树"""
        # 组织拥有者获取完整应用分组结构树
        res = self.client.get(reverse('siteapi:appgroup_tree', args=(self.org.app_group.uid, )))
        self.assertEqual(403, res.status_code)
        # 超级管理员获取完整应用分组结构树
        self.client = self.login('admin', 'admin')
        res = self.client.get(reverse('siteapi:appgroup_tree', args=(self.org.app_group.uid, )))
        expect = {
            'info': {
                'node_uid': self.org.app_group.node_uid,
                'uid': self.org.app_group.uid,
                'name': 'org-应用',
                'remark': ''
            },
            'nodes': [{
                'info': {
                    'node_uid': self.org.default_app_group.node_uid,
                    'uid': self.org.default_app_group.uid,
                    'name': 'org-默认应用',
                    'remark': ''
                },
                'nodes': []
            }]
        }
        self.assertEqual(expect, res.json())

    def test_get_appgroup_child_app(self):
        """测试获取应用分组的成员应用"""
        # 组织拥有者创建一个应用
        self.client.json_post(reverse('siteapi:app_list', args=(self.org.oid, )), data={'name': 'app'}).json()
        res = self.client.get(reverse('siteapi:appgroup_child_app', args=(self.org.default_app_group.uid, )))
        self.assertEqual(1, res.json()['count'])

    def test_adjust_appgroup_child_app(self):
        """测试调整应用分组的成员应用"""
        # 组织拥有者创建两个应用
        app_1 = self.client.json_post(reverse('siteapi:app_list', args=(self.org.oid, )), data={'name': 'app-1'}).json()
        app_2 = self.client.json_post(reverse('siteapi:app_list', args=(self.org.oid, )), data={'name': 'app-2'}).json()
        # 组织拥有者整应用分组的成员应用
        # data = {'app_ids': [app_1['app_id'], app_2['app_id']], 'app_group_uids': [], 'subject': 'add'}
        #   1) 添加应用到该应用分组
        res = self.client.json_patch(reverse('siteapi:appgroup_child_app', args=(self.org.app_group.uid, )),
                                     data={
                                         'app_ids': [app_1['app_id'], app_2['app_id']],
                                         'subject': 'add'
                                     })
        self.assertEqual(2, len(res.json()['apps']))
        #   2) 从该应用分组删除应用
        res = self.client.json_patch(reverse('siteapi:appgroup_child_app', args=(self.org.app_group.uid, )),
                                     data={
                                         'app_ids': [app_1['app_id'], app_2['app_id']],
                                         'subject': 'delete'
                                     })
        self.assertEqual(0, len(res.json()['apps']))
        #   3) 对指定应用按照指定顺序进行排序
        self.client.json_patch(reverse('siteapi:appgroup_child_app', args=(self.org.default_app_group.uid, )),
                               data={
                                   'app_ids': [app_2['app_id'], app_1['app_id']],
                                   'subject': 'sort'
                               })
        res = self.client.get(reverse('siteapi:appgroup_child_app', args=(self.org.default_app_group.uid, )))
        self.assertEqual(2, res.json()['count'])    # 由于获取应用可取多应用分组交集，故排序仅内部实现，未显示到响应结果中 TODO
        #   4) 将一些应用从该应用分组移出，并加到指定应用分组
        res = self.client.json_patch(reverse('siteapi:appgroup_child_app', args=(self.org.default_app_group.uid, )),
                                     data={
                                         'app_ids': [app_1['app_id'], app_2['app_id']],
                                         'app_group_uids': [self.org.app_group.uid],
                                         'subject': 'move_out'
                                     })
        self.assertEqual(0, len(res.json()['apps']))
        #   5) 重置该应用分组的成员应用
        res = self.client.json_patch(reverse('siteapi:appgroup_child_app', args=(self.org.app_group.uid, )),
                                     data={
                                         'app_ids': [],
                                         'subject': 'override'
                                     })
        self.assertEqual(0, len(res.json()['apps']))
