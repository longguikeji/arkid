# pylint: disable=missing-docstring, too-many-lines
'''
test for api about node
'''
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    User, )

NEW_DEPT = {
    "node_uid": "",
    "name": "111",
    "node_scope": [],
    "user_scope": [],
    "manager_group": {
        "nodes": [],
        "users": [],
        "perms": [],
        "apps": [],
        "scope_subject": 1
    },
    "users": []
}

NEW_APP = {"name": "1111", "auth_protocols": [], "index": ""}

NEW_TOP_LEVEL_DEPT = {
    "node_uid": "",
    "name": "新建顶层部门",
    "node_scope": [],
    "user_scope": [],
    "manager_group": {
        "nodes": [],
        "users": [],
        "perms": [],
        "apps": [],
        "scope_subject": 1
    },
    "users": []
}

NEW_USER = {
    "user": {
        "avatar":
        "",
        "email":
        "",
        "employee_number":
        "",
        "gender":
        0,
        "mobile":
        "12312312344",
        "name":
        "dafdafdsaf",
        "position":
        "",
        "private_email":
        "",
        "username":
        "fdsafdsagrda",
        "depts":
        '',
        "roles":
        '',
        "nodes": [{
            "node_uid": "d_bumenyiyi",
            "name": "部门一（一）",
            "node_scope": [],
            "user_scope": [],
            "users": ["13899990006"]
        }],
        "is_settled":
        'false',
        "password":
        "",
        "require_reset_password":
        'false',
        "has_password":
        'false'
    },
    "node_uids": ["d_bumenyiyi"]
}


class GroupManagerViewTestCase(TestCase):
    def test_manager_one_perm_view(self):
        '''
        测试用户 13899990001（部门一admin）设定权限：
        1.管理范围:所在分组及下级分组(部门一及下属)
        2.应用权限:应用二
        3.基础权限:无
        '''
        manager_one = User.objects.filter(username='13899990001').first()
        client = self.login_as(manager_one)

        # 可见部门一及下属部门
        res = client.get(reverse('siteapi:node_tree', args=('d_root', )))
        res = res.json()
        expect = ['部门一（一）', '部门一（二）', '部门一（三）', '部门一（四）', '部门一（五）']
        self.assertEqual(expect, [node['info']['name'] for node in res['nodes'][0]['nodes']])

        # 可编辑应用二
        res_edit_app_yinyonger = client.patch(reverse('siteapi:app_detail', args=('yingyonger', )),
                                              data={'name': '应用二'})
        self.assertEqual(res_edit_app_yinyonger.status_code, HTTP_200_OK)

        # 分组管理可查看节点范围：部门一及其下属
        res_view_phonebook = client.get(reverse('siteapi:node_tree', args=('d_root', )))
        expect = {
            'info': {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': '部门'
            },
            'nodes': [{
                'info': {
                    'dept_id': 2,
                    'node_uid': 'd_bumenyi',
                    'node_subject': 'dept',
                    'uid': 'bumenyi',
                    'name': '部门一（所有人可见）',
                    'remark': ''
                },
                'nodes': [
                    {
                        'info': {
                            'dept_id': 7,
                            'node_uid': 'd_bumenyiyi',
                            'node_subject': 'dept',
                            'uid': 'bumenyiyi',
                            'name': '部门一（一）',
                            'remark': ''
                        },
                        'nodes': []
                    },
                    {
                        'info': {
                            'dept_id': 8,
                            'node_uid': 'd_bumenyier',
                            'node_subject': 'dept',
                            'uid': 'bumenyier',
                            'name': '部门一（二）',
                            'remark': ''
                        },
                        'nodes': []
                    },
                    {
                        'info': {
                            'dept_id': 9,
                            'node_uid': 'd_bumenyisan',
                            'node_subject': 'dept',
                            'uid': 'bumenyisan',
                            'name': '部门一（三）',
                            'remark': ''
                        },
                        'nodes': []
                    },
                    {
                        'info': {
                            'dept_id': 10,
                            'node_uid': 'd_bumenyisi',
                            'node_subject': 'dept',
                            'uid': 'bumenyisi',
                            'name': '部门一（四）',
                            'remark': ''
                        },
                        'nodes': []
                    },
                    {
                        'info': {
                            'dept_id': 11,
                            'node_uid': 'd_bumenyiwu',
                            'node_subject': 'dept',
                            'uid': 'bumenyiwu',
                            'name': '部门一（五）',
                            'remark': ''
                        },
                        'nodes': []
                    },
                ]
            }]
        }
        self.assertEqual(res_view_phonebook.status_code, HTTP_200_OK)
        self.assertEqual(expect, res_view_phonebook.json())

        # 测试部门一admin可见应用范围，可管理应用二
        res = client.get(reverse('siteapi:app_list'))
        res = res.json()
        self.assertEqual(res['results'][0]['uid'], 'yingyonger')
        self.assertEqual(res['count'], 1)

        # 不可查看非权限内用户信息
        res_view_user = client.get(reverse('siteapi:ucenter_user_detail', args=('138999900020', )))
        self.assertEqual(res_view_user.status_code, HTTP_404_NOT_FOUND)

        # 不可创建用户
        res = client.json_post(reverse('siteapi:user_list'), data=NEW_USER)
        self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)

        # 不可编辑部门
        res_edit_dept = client.json_patch(reverse('siteapi:node_child_node', args=('d_root', )))
        self.assertEqual(res_edit_dept.status_code, HTTP_403_FORBIDDEN)

        # 不可编辑分组
        res_edit_node = client.json_patch(reverse('siteapi:node_child_node', args=('g_manager', )))
        self.assertEqual(res_edit_node.status_code, HTTP_403_FORBIDDEN)

        # 不可查看日志
        res_see_log = client.json_patch(reverse('siteapi:log_list'))
        self.assertEqual(res_see_log.status_code, HTTP_403_FORBIDDEN)

        # 不可编辑配置
        res_edit_config = client.json_patch(reverse('siteapi:config'))
        self.assertEqual(res_edit_config.status_code, HTTP_403_FORBIDDEN)

    def test_group_manager_two_views(self):
        '''
        测试用户 13899990002（部门二admin）可见性
        管理范围:部门一、部门二
        其他权限:账号同步、创建应用、创建大类、公司配置、查看日志、创建用户
        应用权限:应用一到十
        '''
        group_manager_two = User.objects.filter(username='13899990002').first()
        client = self.login_as(group_manager_two)

        # 可创建应用
        res = client.json_post(reverse('siteapi:app_list'), data=NEW_APP)
        self.assertEqual(res.status_code, HTTP_201_CREATED)

        # 可查看日志
        res = client.get(reverse('siteapi:log_list'))
        self.assertEqual(res.status_code, HTTP_200_OK)

        # 可查看/修改公司配置
        res = client.get(reverse('siteapi:config'))
        self.assertEqual(res.status_code, HTTP_200_OK)

        # 可添加下级部门
        res = client.json_post(reverse('siteapi:node_child_node', args=('d_bumenyi', )), data=NEW_DEPT)
        self.assertEqual(res.status_code, HTTP_201_CREATED)

        # 可编辑用户信息
        patch_user_data = {
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
        res = client.json_patch(reverse('siteapi:user_detail', args=('13899990006', )), data=patch_user_data)
        self.assertEqual(res.status_code, HTTP_200_OK)

        # 不可添加顶层部门
        res = client.json_post(reverse('siteapi:node_child_node', args=('d_root', )), data=NEW_TOP_LEVEL_DEPT)
        self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)

    def test_group_manager_three_view(self):
        '''
        部门三管理员(13899990003)权限:
        第一组权限：管理范围：部门一，角色三, 账号-部门二admin（13899990002）| 权限：账号同步、创建应用、创建大类
        第二组权限：管理范围：部门一 | 权限：公司配置、查看日志、创建用户
        编辑应用:应用一至十
        '''
        group_manager_three = User.objects.filter(username='13899990003').first()
        client = self.login_as(group_manager_three)

        # 分组管理-部门选项卡，可见部门一
        res_view_phonebook = client.get(reverse('siteapi:node_tree', args=('d_root', )))
        expect = {
            'info': {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': '部门'
            },
            'nodes': [{
                'info': {
                    'dept_id': 2,
                    'node_uid': 'd_bumenyi',
                    'node_subject': 'dept',
                    'uid': 'bumenyi',
                    'name': '部门一（所有人可见）',
                    'remark': ''
                },
                'nodes': [
                    
                ]
            }]
        }
        self.assertEqual(expect, res_view_phonebook.json())

        # 分组管理-角色选项卡，仅可见角色组三
        res = client.get(reverse('siteapi:node_tree', args=('g_role', )))
        expect = {
            'info': {
                'group_id': 5,
                'node_uid': 'g_role',
                'node_subject': 'role',
                'uid': 'role',
                'name': '角色'
            },
            'nodes': [{
                'info': {
                    'group_id': 14,
                    'node_uid': 'g_juesesan',
                    'node_subject': 'role',
                    'uid': 'juesesan',
                    'name': '角色三',
                    'remark': '',
                    'accept_user': True
                },
                'nodes': [{
                    'info': {
                        'group_id': 27,
                        'node_uid': 'g_juesesanyi',
                        'node_subject': 'role',
                        'uid': 'juesesanyi',
                        'name': '角色三（一）',
                        'remark': '',
                        'accept_user': True
                    },
                    'nodes': []
                }]
            }]
        }
        self.assertEqual(res.json(), expect)

        # 可在角色三（一）分组下创建用户
        post_user_data = {
            "user": {
                "avatar": "",
                "email": "",
                "employee_number": "",
                "gender": 0,
                "mobile": "12341231234",
                "name": "1234",
                "position": "",
                "private_email": "",
                "username": "1234",
                "nodes": [{
                    "node_uid": "g_juesesanyi",
                    "name": "角色三（一）",
                    "node_scope": [],
                    "user_scope": [],
                    "users": []
                }],
                "is_settled": 'false',
                "password": "",
                "require_reset_password": 'false',
                "has_password": 'false'
            },
            "node_uids": ["g_juesesanyi"]
        }
        res = client.json_post(reverse('siteapi:user_list'), data=post_user_data)
        self.assertEqual(res.status_code, HTTP_201_CREATED)

        # 可以在角色三分组下创建下级分组
        new_child_node = {
            "node_uid": "",
            "name": "角色三（二）",
            "visibility": 1,
            "node_scope": [],
            "user_scope": [],
            "manager_group": {
                "nodes": [],
                "users": [],
                "perms": [],
                "apps": [],
                "scope_subject": 1
            },
            "users": []
        }
        res = client.json_post(reverse('siteapi:node_child_node', args=('g_juesesan', )), data=new_child_node)
        self.assertEqual(res.status_code, HTTP_201_CREATED)

        # 可编辑管理范围内用户信息
        patch_user_data = {
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
        res = client.json_patch(reverse('siteapi:user_detail', args=('13899990006', )), data=patch_user_data)
        self.assertEqual(res.status_code, HTTP_200_OK)

        # 不可编辑管理范围外用户信息
        patch_user_data = {
            "avatar": "",
            "email": "",
            "employee_number": "",
            "gender": 0,
            "mobile": "13899990011",
            "name": "部门二一user",
            "position": "",
            "private_email": "",
            "username": "13899990011",
            "depts": '',
            "roles": '',
            "nodes": [{
                "node_uid": "d_bumeneryi",
                "name": "部门二（一）",
                "node_scope": [],
                "user_scope": [],
                "users": []
            }],
            "is_settled": 'true',
            "require_reset_password": 'false',
            "has_password": 'true'
        }
        res = client.json_patch(reverse('siteapi:user_detail', args=('13899990011', )), data=patch_user_data)
        self.assertEqual(res.status_code, HTTP_404_NOT_FOUND)
