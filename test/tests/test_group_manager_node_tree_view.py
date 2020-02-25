# pylint: disable=missing-docstring
'''
test for api about node
'''
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    User, )

USER_ONE = {
    "avatar":
    "",
    "email":
    "",
    "employee_number":
    "",
    "gender":
    0,
    "mobile":
    "13899990001",
    "name":
    "部门一admin",
    "position":
    "",
    "private_email":
    "",
    "username":
    "13899990001",
    "depts":
    '',
    "roles":
    '',
    "nodes": [{
        "node_uid": "g_wdexnpal",
        "name": "wdexnpal",
        "node_scope": [],
        "user_scope": [],
        "manager_group": {
            "nodes": [],
            "users": [],
            "perms": [],
            "apps": [''],
            "scope_subject": 1
        },
        "users": []
    }, {
        "node_uid": "d_bumenyi",
        "name": "部门一（所有人可见）",
        "node_scope": [],
        "user_scope": [],
        "users": []
    }],
    "is_settled":
    'true',
    "require_reset_password":
    'false',
    "has_password":
    'true'
}
USER_SIX = {
    "avatar": "",
    "email": "",
    "employee_number": "",
    "gender": 0,
    "mobile": "13899990006",
    "name": "部门一一user",
    "position": "",
    "private_email": "",
    "username": "13899990006",
    "depts": '',
    "roles": '',
    "nodes": [{
        "node_uid": "d_bumenyiyi",
        "name": "部门一（一）",
        "node_scope": [],
        "user_scope": [],
        "users": []
    }],
    "is_settled": 'true',
    "require_reset_password": 'false',
    "has_password": 'true'
}


class GroupManagerViewTestCase(TestCase):
    def test_manager_one_perm_view(self):
        '''
        测试用户13899990001(部门一admin)可见范围
        管理范围:所在分组及下级
        其他权限:空
        应用权限:应用二
        '''
        manager_one = User.objects.filter(username=13899990001).first()
        client = self.login_as(manager_one)

        # 分组管理可见本部门及下属6人
        res = client.get(reverse('siteapi:node_tree', args=('d_root', )), data={'user_required': True})
        self.assertEqual(res.json()['headcount'], 6)
        expect = ['13899990006', '13899990007', '13899990008', '13899990009', '13899990010']
        self.assertEqual([j['username'] for i in res.json()['nodes'][0]['nodes'] for j in i['users']], expect)

        # 账户管理不可见，因为分组管理已经包括了可管理人员
        res = client.get(reverse('siteapi:user_list'))
        self.assertEqual(res.json()['count'], 0)
        expect = []
        self.assertEqual([i['user']['username'] for i in res.json()['results']], expect)

        # /user/13899990006, 可修改管理人员
        res = client.json_patch(reverse('siteapi:user_detail', args=('13899990006', )), data=USER_SIX)
        self.assertEqual(res.status_code, HTTP_200_OK)

        # /user/13899990007, 可删除管理人员
        res = client.delete(reverse('siteapi:user_detail', args=('13899990007', )))
        self.assertEqual(res.status_code, HTTP_204_NO_CONTENT)

    def test_manager_two_perm_view(self):
        '''
        测试用户 13899990002（部门二admin）可见性
        管理范围:部门一、部门二
        其他权限:账号同步、创建应用、创建大类、公司配置、查看日志、创建用户
        应用权限:应用一到十
        '''
        manager_two = User.objects.filter(username=13899990002).first()
        client = self.login_as(manager_two)

        # 指定节点2个，分组管理只能看到2人
        res = client.get(reverse('siteapi:node_tree', args=('d_root', )), data={'user_required': True})
        expect = ['13899990001', '13899990002']
        self.assertEqual(res.json()['headcount'], 2)
        self.assertEqual([j['username'] for i in res.json()['nodes'] for j in i['users']], expect)

    def test_manager_three_user_list_view(self):    # pylint: disable=invalid-name
        '''
        部门四管理员(13899990004)权限:
        第一组权限：管理范围：部门一、部门一admin、部门二admin | 权限：账号同步、创建应用、创建大类、公司配置、查看日志、创建用户
        第二组权限：管理范围：部门二、部门三admin、部门四admin | 权限：应用一、应用二、应用三
        '''
        manager_four = User.objects.filter(username='13899990004').first()
        client = self.login_as(manager_four)

        # user_list可见14人,包括部门一全部6人，部门二6人,部门三管理员，部门四管理员
        res = client.get(reverse('siteapi:user_list'))
        expect = [
            '13899990001', '13899990002', '13899990003', '13899990004', '13899990006', '13899990007', '13899990008',
            '13899990009', '13899990010', '13899990011', '13899990012', '13899990013', '13899990014', '13899990015'
        ]
        self.assertEqual(res.json()['count'], 14)
        self.assertEqual([i['user']['username'] for i in res.json()['results']], expect)

        # /user/13899990001, 可修改直接管理人员
        res = client.json_patch(reverse('siteapi:user_detail', args=('13899990001', )), data=USER_ONE)
        self.assertEqual(res.status_code, HTTP_200_OK)

        # /user/13899990006, 不可修改间接管理人员，但是可见
        res = client.json_patch(reverse('siteapi:user_detail', args=('13899990006', )), data=USER_SIX)
        self.assertEqual(res.status_code, HTTP_404_NOT_FOUND)

        # /user/13899990007, 不可删除间接管理人员，但是可见
        res = client.delete(reverse('siteapi:user_detail', args=('13899990007', )))
        self.assertEqual(res.status_code, HTTP_404_NOT_FOUND)
