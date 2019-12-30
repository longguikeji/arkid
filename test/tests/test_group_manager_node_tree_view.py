# pylint: disable=missing-docstring
'''
test for api about node
'''
from django.urls import reverse
from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    User, )


class GroupManagerViewTestCase(TestCase):
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
