# pylint: disable=too-many-lines
'''
测试普通用户可见性视图
'''
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from siteapi.v1.tests import TestCase
from oneid_meta.models import User


class NormalUserViewTestCase(TestCase):
    '''
    测试普通用户通讯录及应用可见性
    '''
    def test_manager_one_ucenter_view(self):
        '''
        测试用户 13899990001（部门一admin）普通用户视图
        设定权限：
        1.管理范围:所在分组及下级分组(部门一及下属)
        2.应用权限:应用二
        3.基础权限:无
        '''
        manager_one = User.objects.filter(username='13899990001').first()
        client = self.login_as(manager_one)

        # 不可查看非权限内用户信息
        res_view_user = client.get(reverse('siteapi:ucenter_user_detail', args=('138999900020', )))
        self.assertEqual(res_view_user.status_code, HTTP_404_NOT_FOUND)

    def test_dept_one_normal_users_app_view(self):    # pylint: disable=invalid-name
        '''
        应用十：部门权限 > 白名单 > 部门一（成员包括13899990007-13899990011）
        '''
        user = User.objects.filter(username=13899990007).first()
        client = self.login_as(user)
        res = client.get(reverse('siteapi:ucenter_app_list'))
        self.assertEqual(res.json()['results'][0]['uid'], 'yingyongshi')

    def app_black_list(self):
        '''
        黑名单：部门一成员13899990006为黑名单人员，不可见应用十
        '''
        user = User.objects.filter(username='13899990006')
        client = self.login_as(user)
        res = client.get(reverse('siteapi:ucenter_app_list'))
        self.assertEqual(res.json()['count'], 0)

    def test_normal_user_phonebook_view(self):
        '''
        测试用户请求通讯录正常
        '''
        # 部门一管理员可见通讯录,可见部门一到五及其可见部门人员，共6人
        user = User.objects.filter(username='13899990001').first()
        client = self.login_as(user)
        res = client.get(reverse('siteapi:ucenter_node_tree', args=('d_root', )), data={'user_required': True})
        manager_one_phone_book_list = {
            'info': {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': '部门',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改'
            },
            'users': [],
            'nodes': [{
                'info': {
                    'dept_id': 2,
                    'node_uid': 'd_bumenyi',
                    'node_subject': 'dept',
                    'uid': 'bumenyi',
                    'name': '部门一（所有人可见）',
                    'remark': ''
                },
                'users': [{
                    'user_id': 4,
                    'username': '13899990001',
                    'name': '部门一admin'
                }],
                'nodes': [{
                    'info': {
                        'dept_id': 7,
                        'node_uid': 'd_bumenyiyi',
                        'node_subject': 'dept',
                        'uid': 'bumenyiyi',
                        'name': '部门一（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 9,
                        'username': '13899990006',
                        'name': '部门一一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                2
            }, {
                'info': {
                    'dept_id': 3,
                    'node_uid': 'd_bumener',
                    'node_subject': 'dept',
                    'uid': 'bumener',
                    'name': '部门二（组内可见下属不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 12,
                        'node_uid': 'd_bumeneryi',
                        'node_subject': 'dept',
                        'uid': 'bumeneryi',
                        'name': '部门二（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 15,
                        'username': '13899990011',
                        'name': '部门二一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 4,
                    'node_uid': 'd_bumensan',
                    'node_subject': 'dept',
                    'uid': 'bumensan',
                    'name': '部门三（组内成员及下属分组可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 17,
                        'node_uid': 'd_bumensanyi',
                        'node_subject': 'dept',
                        'uid': 'bumensanyi',
                        'name': '部门三（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 20,
                        'username': '13899990016',
                        'name': '部门三一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 5,
                    'node_uid': 'd_bumensisuoyourenbukejian',
                    'node_subject': 'dept',
                    'uid': 'bumensisuoyourenbukejian',
                    'name': '部门四（所有人不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 18,
                        'node_uid': 'd_bumensiyi',
                        'node_subject': 'dept',
                        'uid': 'bumensiyi',
                        'name': '部门四（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 25,
                        'username': '13899990021',
                        'name': '部门四一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 6,
                    'node_uid': 'd_bumenwubufenrenkejian',
                    'node_subject': 'dept',
                    'uid': 'bumenwubufenrenkejian',
                    'name': '部门五（部分人可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 19,
                        'node_uid': 'd_bumenwuyi',
                        'node_subject': 'dept',
                        'uid': 'bumenwuyi',
                        'name': '部门五（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 30,
                        'username': '13899990026',
                        'name': '部门五一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }],
            'headcount':
            6
        }
        self.assertEqual(res.json(), manager_one_phone_book_list)
        self.assertEqual(res.json()['headcount'], 6)

        # 部门一成员可见通讯录6人
        dept_one_user_phone_book = {
            'info': {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': '部门',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改'
            },
            'users': [],
            'nodes': [{
                'info': {
                    'dept_id': 2,
                    'node_uid': 'd_bumenyi',
                    'node_subject': 'dept',
                    'uid': 'bumenyi',
                    'name': '部门一（所有人可见）',
                    'remark': ''
                },
                'users': [{
                    'user_id': 4,
                    'username': '13899990001',
                    'name': '部门一admin'
                }],
                'nodes': [{
                    'info': {
                        'dept_id': 7,
                        'node_uid': 'd_bumenyiyi',
                        'node_subject': 'dept',
                        'uid': 'bumenyiyi',
                        'name': '部门一（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 9,
                        'username': '13899990006',
                        'name': '部门一一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                2
            }, {
                'info': {
                    'dept_id': 3,
                    'node_uid': 'd_bumener',
                    'node_subject': 'dept',
                    'uid': 'bumener',
                    'name': '部门二（组内可见下属不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 12,
                        'node_uid': 'd_bumeneryi',
                        'node_subject': 'dept',
                        'uid': 'bumeneryi',
                        'name': '部门二（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 15,
                        'username': '13899990011',
                        'name': '部门二一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 4,
                    'node_uid': 'd_bumensan',
                    'node_subject': 'dept',
                    'uid': 'bumensan',
                    'name': '部门三（组内成员及下属分组可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 17,
                        'node_uid': 'd_bumensanyi',
                        'node_subject': 'dept',
                        'uid': 'bumensanyi',
                        'name': '部门三（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 20,
                        'username': '13899990016',
                        'name': '部门三一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 5,
                    'node_uid': 'd_bumensisuoyourenbukejian',
                    'node_subject': 'dept',
                    'uid': 'bumensisuoyourenbukejian',
                    'name': '部门四（所有人不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 18,
                        'node_uid': 'd_bumensiyi',
                        'node_subject': 'dept',
                        'uid': 'bumensiyi',
                        'name': '部门四（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 25,
                        'username': '13899990021',
                        'name': '部门四一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 6,
                    'node_uid': 'd_bumenwubufenrenkejian',
                    'node_subject': 'dept',
                    'uid': 'bumenwubufenrenkejian',
                    'name': '部门五（部分人可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 19,
                        'node_uid': 'd_bumenwuyi',
                        'node_subject': 'dept',
                        'uid': 'bumenwuyi',
                        'name': '部门五（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 30,
                        'username': '13899990026',
                        'name': '部门五一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }],
            'headcount':
            6
        }
        user = User.objects.filter(username='13899990006').first()
        client = self.login_as(user)
        res = client.get(reverse('siteapi:ucenter_node_tree', args=('d_root', )), data={'user_required': True})
        self.assertEqual(res.json(), dept_one_user_phone_book)

        # 部门五无权限用户可见通讯录6人
        user = User.objects.filter(username='13899990005').first()
        client = self.login_as(user)
        res = client.get(reverse('siteapi:ucenter_node_tree', args=('d_root', )), data={'user_required': True})
        no_perm_user_phone_book = {
            'info': {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': '部门',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改'
            },
            'users': [],
            'nodes': [{
                'info': {
                    'dept_id': 2,
                    'node_uid': 'd_bumenyi',
                    'node_subject': 'dept',
                    'uid': 'bumenyi',
                    'name': '部门一（所有人可见）',
                    'remark': ''
                },
                'users': [{
                    'user_id': 4,
                    'username': '13899990001',
                    'name': '部门一admin'
                }],
                'nodes': [{
                    'info': {
                        'dept_id': 7,
                        'node_uid': 'd_bumenyiyi',
                        'node_subject': 'dept',
                        'uid': 'bumenyiyi',
                        'name': '部门一（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 9,
                        'username': '13899990006',
                        'name': '部门一一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                2
            }, {
                'info': {
                    'dept_id': 3,
                    'node_uid': 'd_bumener',
                    'node_subject': 'dept',
                    'uid': 'bumener',
                    'name': '部门二（组内可见下属不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 12,
                        'node_uid': 'd_bumeneryi',
                        'node_subject': 'dept',
                        'uid': 'bumeneryi',
                        'name': '部门二（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 15,
                        'username': '13899990011',
                        'name': '部门二一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 4,
                    'node_uid': 'd_bumensan',
                    'node_subject': 'dept',
                    'uid': 'bumensan',
                    'name': '部门三（组内成员及下属分组可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 17,
                        'node_uid': 'd_bumensanyi',
                        'node_subject': 'dept',
                        'uid': 'bumensanyi',
                        'name': '部门三（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 20,
                        'username': '13899990016',
                        'name': '部门三一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 5,
                    'node_uid': 'd_bumensisuoyourenbukejian',
                    'node_subject': 'dept',
                    'uid': 'bumensisuoyourenbukejian',
                    'name': '部门四（所有人不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 18,
                        'node_uid': 'd_bumensiyi',
                        'node_subject': 'dept',
                        'uid': 'bumensiyi',
                        'name': '部门四（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 25,
                        'username': '13899990021',
                        'name': '部门四一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 6,
                    'node_uid': 'd_bumenwubufenrenkejian',
                    'node_subject': 'dept',
                    'uid': 'bumenwubufenrenkejian',
                    'name': '部门五（部分人可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 19,
                        'node_uid': 'd_bumenwuyi',
                        'node_subject': 'dept',
                        'uid': 'bumenwuyi',
                        'name': '部门五（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 30,
                        'username': '13899990026',
                        'name': '部门五一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }],
            'headcount':
            6
        }
        self.assertEqual(res.json(), no_perm_user_phone_book)

    def test_normal_user_view(self):
        '''
        测试部门一用户（13899990007）视图及权限,权限:无权限
        '''
        # 不可见应用
        no_perm_user = User.objects.filter(username='13899990007').first()
        client = self.login_as(no_perm_user)
        res = client.get(reverse('siteapi:app_list'))
        self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)

        # 可查看用户信息
        res_view_user = client.get(reverse('siteapi:ucenter_user_detail', args=('13899990002', )))
        self.assertEqual(res_view_user.status_code, HTTP_200_OK)

    def test_dept_fourtwo_user_view(self):
        '''
        测试部门四二成员可见通讯录：
        '''
        dept_fourtwo_user = User.objects.filter(username='13899990022').first()
        client = self.login_as(dept_fourtwo_user)

        # 可见7人，包括自身，其他6人为所有人可见部门成员
        res = client.get(reverse('siteapi:ucenter_node_tree', args=('d_root', )), data={'user_required': True})
        phone_book = {
            'info': {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': '部门',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改'
            },
            'users': [],
            'nodes': [{
                'info': {
                    'dept_id': 2,
                    'node_uid': 'd_bumenyi',
                    'node_subject': 'dept',
                    'uid': 'bumenyi',
                    'name': '部门一（所有人可见）',
                    'remark': ''
                },
                'users': [{
                    'user_id': 4,
                    'username': '13899990001',
                    'name': '部门一admin'
                }],
                'nodes': [{
                    'info': {
                        'dept_id': 7,
                        'node_uid': 'd_bumenyiyi',
                        'node_subject': 'dept',
                        'uid': 'bumenyiyi',
                        'name': '部门一（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 9,
                        'username': '13899990006',
                        'name': '部门一一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                2
            }, {
                'info': {
                    'dept_id': 3,
                    'node_uid': 'd_bumener',
                    'node_subject': 'dept',
                    'uid': 'bumener',
                    'name': '部门二（组内可见下属不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 12,
                        'node_uid': 'd_bumeneryi',
                        'node_subject': 'dept',
                        'uid': 'bumeneryi',
                        'name': '部门二（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 15,
                        'username': '13899990011',
                        'name': '部门二一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 4,
                    'node_uid': 'd_bumensan',
                    'node_subject': 'dept',
                    'uid': 'bumensan',
                    'name': '部门三（组内成员及下属分组可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 17,
                        'node_uid': 'd_bumensanyi',
                        'node_subject': 'dept',
                        'uid': 'bumensanyi',
                        'name': '部门三（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 20,
                        'username': '13899990016',
                        'name': '部门三一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }, {
                'info': {
                    'dept_id': 5,
                    'node_uid': 'd_bumensisuoyourenbukejian',
                    'node_subject': 'dept',
                    'uid': 'bumensisuoyourenbukejian',
                    'name': '部门四（所有人不可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 18,
                        'node_uid': 'd_bumensiyi',
                        'node_subject': 'dept',
                        'uid': 'bumensiyi',
                        'name': '部门四（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 25,
                        'username': '13899990021',
                        'name': '部门四一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }, {
                    'info': {
                        'dept_id': 24,
                        'node_uid': 'd_bumensier',
                        'node_subject': 'dept',
                        'uid': 'bumensier',
                        'name': '部门四（二）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 26,
                        'username': '13899990022',
                        'name': '部门四二user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                2
            }, {
                'info': {
                    'dept_id': 6,
                    'node_uid': 'd_bumenwubufenrenkejian',
                    'node_subject': 'dept',
                    'uid': 'bumenwubufenrenkejian',
                    'name': '部门五（部分人可见）'
                },
                'users': [],
                'nodes': [{
                    'info': {
                        'dept_id': 19,
                        'node_uid': 'd_bumenwuyi',
                        'node_subject': 'dept',
                        'uid': 'bumenwuyi',
                        'name': '部门五（一）',
                        'remark': ''
                    },
                    'users': [{
                        'user_id': 30,
                        'username': '13899990026',
                        'name': '部门五一user'
                    }],
                    'nodes': [],
                    'headcount': 1
                }],
                'headcount':
                1
            }],
            'headcount':
            7
        }
        self.assertEqual(res.json(), phone_book)
        self.assertEqual(res.json()['headcount'], 7)

        # 可查看其他组内用户信息
        res_view_user = client.get(reverse('siteapi:ucenter_user_detail', args=('13899990012', )))
        self.assertEqual(res_view_user.status_code, HTTP_200_OK)
