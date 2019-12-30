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
        self.assertEqual(res.json()['headcount'], 2)

    def test_manager_three_user_list_view(self):    # pylint: disable=invalid-name
        '''
        部门三管理员(13899990003)权限:
        第一组权限：管理范围：部门一，角色三, 账号-部门二admin（13899990002）| 权限：账号同步、创建应用、创建大类
        第二组权限：管理范围：部门一 | 权限：公司配置、查看日志、创建用户
        编辑应用:应用一至十
        '''
        manager_three = User.objects.filter(username='13899990003').first()
        client = self.login_as(manager_three)

        # user_list可见7人,包括部门一全部6人，用户13899990002
        res = client.get(reverse('siteapi:user_list'))
        self.assertEqual(res.json()['count'], 7)
