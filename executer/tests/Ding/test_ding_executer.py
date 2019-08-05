"""
钉钉数据操作单元测试用例
"""
# pylint: disable=missing-docstring
# pylint: disable=no-self-use

from unittest import TestCase
from unittest import mock
from unittest.mock import call
from unittest.mock import patch
from executer.Ding import DingExecuter, DEFAULT_DEPT

USER_INFO = {
    'username': 'test1',
    'ding_user': {
        'account': '1521035',
        'data': '{"name": "abc","tel": "020-121", "position": "北京"}'
    }
}

DEPT_INFO = {
    'name': 'new_name',
    'remark': 'new_remark',
    'uid': '23',
    'ding_dept': {
        'uid': 1,
        'data': '{"key": "val"}',
    }
}

GROUP_ACCEPT_USER_INFO = {'name': 'group_1', 'uid': 10, 'parent_uid': 1, 'accept_user': True}

GROUP_NO_USER_INFO = {'name': 'group_1', 'uid': 10, 'parent_uid': 1, 'accept_user': False}


class TestDingExecuter(TestCase):
    @patch('executer.Ding.User')
    @patch('executer.Ding.UserManager')
    def test_create_user(self, mock_user_manager, mock_user):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_user_instance = mock_user.valid_objects
        mock_user_manager_instance.add_user.return_value = {'userid': '12'}
        ding_executer = DingExecuter()
        ret = ding_executer.create_user(USER_INFO)
        mock_user_manager_instance.add_user.assert_called_with('abc', '1521035', '1', tel='020-121', position='北京')

        mock_user_instance.filter.assert_called_with(username=USER_INFO['username'])
        self.assertEqual(ret, '12')

    @patch('executer.Ding.User')
    @patch('executer.Ding.UserManager')
    def test_update_user(self, mock_user_manager, mock_user):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_user.ding_user.uid = '10'
        ding_executer = DingExecuter()
        ding_executer.update_user(mock_user, USER_INFO)
        mock_user_manager_instance.update_user.assert_called_with('10', name='abc', tel='020-121', position='北京')

    @patch('executer.Ding.UserManager')
    def test_delete_user(self, mock_user_manager):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_user_1 = mock.Mock()
        mock_user_2 = mock.Mock()
        mock_user_1.ding_user.uid = '10'
        mock_user_2.ding_user.uid = '20'
        users = [mock_user_1, mock_user_2]
        ding_executer = DingExecuter()
        ding_executer.delete_users(users)
        expected = [call('10'), call('20')]
        self.assertEqual(mock_user_manager_instance.delete_user.call_args_list, expected)

    @patch('executer.Ding.Dept')
    @patch('executer.Ding.DepartmentManager')
    def test_create_dept(self, mock_dept_manager, mock_dept):
        mock_dept_manager_instance = mock_dept_manager.return_value
        mock_dept_instance = mock_dept.valid_objects
        mock_dept_manager_instance.create_dep.return_value = {'id': '12'}
        ding_executer = DingExecuter()
        ret = ding_executer.create_dept(DEPT_INFO)
        mock_dept_manager_instance.create_dep.assert_called_with(
            DEFAULT_DEPT,
            'new_name',
            key='val',
        )

        mock_dept_instance.filter.assert_called_with(uid=DEPT_INFO['uid'])
        self.assertEqual(ret, '12')

    @patch('executer.Ding.DepartmentManager')
    def test_update_dept(self, mock_dept_manager):
        mock_dept_manager_instance = mock_dept_manager.return_value
        dept = mock.Mock()
        dept.ding_dept.uid = '10'
        ding_executer = DingExecuter()
        ding_executer.update_dept(dept, DEPT_INFO)
        mock_dept_manager_instance.update_dep.assert_called_with(
            '10',
            key='val',
        )

    @patch('executer.Ding.DepartmentManager')
    def test_delete_dept(self, mock_dept_manager):
        mock_dept_manager_instance = mock_dept_manager.return_value
        dept = mock.Mock()
        dept.ding_dept.uid = '10'
        ding_executer = DingExecuter()
        ding_executer.delete_dept(dept)
        mock_dept_manager_instance.delete_dep.assert_called_with('10')

    @patch('executer.Ding.DepartmentManager')
    def test_add_dept_to_dept(self, mock_dept_manager):
        mock_dept_manager_instance = mock_dept_manager.return_value
        dept = mock.Mock()
        dept.ding_dept.uid = '10'
        parent_dept = mock.Mock()
        parent_dept.ding_dept.uid = '1'
        ding_executer = DingExecuter()
        ding_executer.add_dept_to_dept(dept, parent_dept)
        mock_dept_manager_instance.update_dep.assert_called_with('10', parentid='1')

    @patch('executer.Ding.DepartmentManager')
    def test_move_dept_to_dept(self, mock_dept_manager):
        mock_dept_manager_instance = mock_dept_manager.return_value
        dept = mock.Mock()
        dept.ding_dept.uid = '10'
        parent_dept = mock.Mock()
        parent_dept.ding_dept.uid = '1'
        ding_executer = DingExecuter()
        ding_executer.move_dept_to_dept(dept, parent_dept)
        mock_dept_manager_instance.update_dep.assert_called_with('10', parentid='1')

    @patch('executer.Ding.DeptMember')
    @patch('executer.Ding.UserManager')
    def test_add_user_to_depts(self, mock_user_manager, mock_dept_mem):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_dept_mem_instance = mock_dept_mem.valid_objects
        mock_dept_item_1 = mock.Mock()
        mock_dept_item_1.owner.ding_dept.uid = 1
        mock_dept_item_2 = mock.Mock()
        mock_dept_item_2.owner.ding_dept.uid = 2
        mock_dept_mem_instance.filter.return_value = [mock_dept_item_1, mock_dept_item_2]

        mock_user = mock.Mock()
        mock_user.ding_user.uid = 'ab'
        depts = [3, 4]
        ding_executer = DingExecuter()
        ding_executer.add_user_to_depts(mock_user, depts)
        mock_dept_mem_instance.filter.assert_called_with(user=mock_user)
        mock_user_manager_instance.update_user.assert_called_with('ab', department=[3, 4, 1, 2])

    @patch('executer.Ding.UserManager')
    def test_delete_user_from_depts(self, mock_user_manager):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_user_manager_instance.get_user_detail.return_value = {'department': [1, 2, 3]}

        mock_user = mock.Mock()
        mock_user.ding_user.uid = 'ab'
        mock_dept_item_1 = mock.Mock()
        mock_dept_item_1.ding_dept.uid = 2
        mock_dept_item_2 = mock.Mock()
        mock_dept_item_2.ding_dept.uid = 3

        ding_executer = DingExecuter()
        ding_executer.delete_user_from_depts(mock_user, [mock_dept_item_1, mock_dept_item_2])
        mock_user_manager_instance.get_user_detail.assert_called_with('ab')
        mock_user_manager_instance.update_user('ab', department=[1])

    @patch('executer.Ding.UserManager')
    def test_delete_users_from_dept(self, mock_user_manager):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_user_manager_instance.get_user_detail.return_value = {'department': [3, 4, 5]}

        mock_user_1 = mock.Mock()
        mock_user_1.ding_user.uid = 'ab'
        mock_user_2 = mock.Mock()
        mock_user_2.ding_user.uid = 'cd'
        mock_dept_item = mock.Mock()
        mock_dept_item.ding_dept.uid = 3
        ding_execute = DingExecuter()
        ding_execute.delete_users_from_dept([mock_user_1, mock_user_2], mock_dept_item)

        expected_get_detail = [call('ab'), call('cd')]
        self.assertEqual(mock_user_manager_instance.get_user_detail.call_args_list, expected_get_detail)

        expected_update = [call('ab', department=[4, 5]), call('cd', department=[4, 5])]
        self.assertEqual(mock_user_manager_instance.update_user.call_args_list, expected_update)

    @patch('executer.Ding.DeptMember')
    @patch('executer.Ding.UserManager')
    def test_add_users_to_dept(self, mock_user_manager, mock_dept_mem):
        mock_user_manager_instance = mock_user_manager.return_value
        mock_dept_mem_instance = mock_dept_mem.valid_objects
        mock_dept_item_1 = mock.Mock()
        mock_dept_item_1.owner.uid = 1
        mock_dept_item_2 = mock.Mock()
        mock_dept_item_2.owner.uid = 2
        mock_dept_mem_instance.filter.return_value = [mock_dept_item_1, mock_dept_item_2]

        mock_user_1 = mock.Mock()
        mock_user_1.ding_user.uid = 'ab'
        mock_user_2 = mock.Mock()
        mock_user_2.ding_user.uid = 'cd'
        mock_dept_item = mock.Mock()
        mock_dept_item.ding_dept.uid = 3
        ding_execute = DingExecuter()
        ding_execute.add_users_to_dept([mock_user_1, mock_user_2], mock_dept_item)

        expected_update = [call('ab', department=[1, 2, 3]), call('cd', department=[1, 2, 3])]
        self.assertEqual(mock_user_manager_instance.update_user.call_args_list, expected_update)

    @patch('executer.Ding.Group')
    @patch('executer.Ding.RoleManager')
    def test_create_group(self, mock_group_manager, mock_group):
        mock_group_manager_instance = mock_group_manager.return_value

        mock_group_item = mock.Mock()
        mock_group_item.ding_group.uid = 5
        mock_group.return_value.valid_objects.get_queryset.filter.first.return_value = mock_group_item
        mock_group_manager_instance.create_role.return_value = {'roleId': 3}

        ding_executer = DingExecuter()
        ret = ding_executer.create_group(GROUP_ACCEPT_USER_INFO)

        mock_group_manager_instance.create_role.assert_called_with(GROUP_ACCEPT_USER_INFO['name'],
                                                                   GROUP_ACCEPT_USER_INFO['parent_uid'])
        self.assertEqual(ret, 3)

        mock_group_manager_instance.create_role_group.return_value = {'groupId': 2}
        ret_no_user = ding_executer.create_group(GROUP_NO_USER_INFO)
        mock_group_manager_instance.create_role_group.assert_called_with(GROUP_NO_USER_INFO['name'], )
        self.assertEqual(ret_no_user, 2)

    @patch('executer.Ding.RoleManager')
    def test_update_group(self, mock_group_manager):
        mock_group_instance = mock_group_manager.return_value

        mock_group = mock.Mock()
        mock_group.ding_group = {'uid': 1}

        group_info = {'name': 'test_group'}

        ding_executer = DingExecuter()
        ding_executer.update_group(mock_group, group_info)
        mock_group_instance.update_role.assert_called_with(group_info['name'], mock_group.ding_group['uid'])

    @patch('executer.Ding.RoleManager')
    def test_delete_group(self, mock_group_manager):
        mock_group_instance = mock_group_manager.return_value

        mock_group = mock.Mock()
        mock_group.ding_group.uid = 2
        ding_executer = DingExecuter()
        ding_executer.delete_group(mock_group)
        mock_group_instance.delete_role.assert_called_with(2)

    @patch('executer.Ding.RoleManager')
    def test_add_users_to_group(self, mock_group_manager):
        mock_group_instance = mock_group_manager.return_value

        mock_group = mock.Mock()
        mock_group.ding_group.uid = 2
        mock_user_1 = mock.Mock()
        mock_user_2 = mock.Mock()
        mock_user_1.ding_user.uid = '1'
        mock_user_2.ding_user.uid = '2'
        ding_executer = DingExecuter()
        ding_executer.add_users_to_group([mock_user_1, mock_user_2], mock_group)
        mock_group_instance.add_users_roles.assert_called_with('2', '1,2')

    @patch('executer.Ding.RoleManager')
    def test_add_user_to_groups(self, mock_group_manager):
        mock_group_instance = mock_group_manager.return_value

        mock_group_1 = mock.Mock()
        mock_group_2 = mock.Mock()
        mock_group_1.ding_group.uid = 1
        mock_group_2.ding_group.uid = 2
        mock_user = mock.Mock()
        mock_user.ding_user.uid = '1'

        ding_executer = DingExecuter()
        ding_executer.add_user_to_groups(mock_user, [mock_group_1, mock_group_2])
        mock_group_instance.add_users_roles.assert_called_with('1,2', '1')

    @patch('executer.Ding.RoleManager')
    def test_delete_user_from_groups(self, mock_group_manager):
        mock_group_instance = mock_group_manager.return_value

        mock_group_1 = mock.Mock()
        mock_group_2 = mock.Mock()
        mock_group_1.ding_group.uid = 1
        mock_group_2.ding_group.uid = 2
        mock_user = mock.Mock()
        mock_user.ding_user.uid = '1'

        ding_executer = DingExecuter()
        ding_executer.delete_user_from_groups(mock_user, [mock_group_1, mock_group_2])
        mock_group_instance.delete_users_roles.assert_called_with('1,2', '1')

    @patch('executer.Ding.RoleManager')
    def test_delete_users_from_group(self, mock_group_manager):
        mock_group_instance = mock_group_manager.return_value

        mock_group = mock.Mock()
        mock_group.ding_group.uid = 2
        mock_user_1 = mock.Mock()
        mock_user_2 = mock.Mock()
        mock_user_1.ding_user.uid = '1'
        mock_user_2.ding_user.uid = '2'
        ding_executer = DingExecuter()
        ding_executer.delete_users_from_group([mock_user_1, mock_user_2], mock_group)
        mock_group_instance.delete_users_roles.assert_called_with('2', '1,2')
