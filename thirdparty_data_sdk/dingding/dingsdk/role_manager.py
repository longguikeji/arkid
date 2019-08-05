"""
Dingding role manage api
"""

from thirdparty_data_sdk.dingding.dingsdk import constants
from thirdparty_data_sdk.dingding.dingsdk.request_manager import RequestManager


class RoleManager():
    """
    Role Manage class, init with AccessTokenManager instance
    """

    def __init__(self, token_manager):
        """
        init the RoleManager
        :param AccessTokenManager token_manager: instance of AccessTokenManager
        """
        self.token_manager = token_manager
        self.request_manager = RequestManager()

    def get_roles_list(self, size, offset):
        """
        获取角色列表
        :param size: Number 分页大小，最大值200
        :param offset: Number 分页偏移
        :return: {
            'errcode':0,
            'errmsg':'ok',
            'result':{
                'hasMore':false,
                'list':[
                    {
                        'name':'默认',
                        'groupId':1,
                        'roles':[
                            {
                                'name':'管理员',
                                'id':1
                            }
                        ]
                    }
                ]
            }
        }
        """

        extra_data = {
            'size': size,
            'offset': offset,
        }

        return self.request_manager.post(
            request_url=constants.ROLE_GET_ROLES_LIST,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def get_role_userlist(self, role_id, size, offset):
        """
         获取角色下的员工列表
        :param role_id: Number 角色ID
        :param size: Number 分页大小
        :param offset: 分页偏移
        :return:{
            'errcode':0,
            'errmsg':'ok',
            'result':{
                'hasMore':false,
                'nextCursor':100,#下次拉取数据的游标
                'list':[
                    {
                        'userid':'manager7978',
                        'name':'小钉'
                    }
                ]
            }
        }
        """
        extra_data = {
            'role_id': role_id,
            'size': size,
            'offset': offset,
        }

        return self.request_manager.post(
            request_url=constants.ROLE_GET_ROLE_USERLIST,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def get_role_group(self, group_id):
        """
        获取角色组
        :param group_id:Number 角色组Id
        :return:{
            'role_group':{
                'roles':[
                    {
                        'role_id':1,
                        'role_name':'出纳'
                    }
                ],
                'group_name':'财务'
            },
            'errcode':1,
            'errmsg':'ok'
        }
        """

        extra_data = {'group_id': group_id}

        return self.request_manager.post(
            request_url=constants.ROLE_GET_ROLE_GROUP,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def get_role_detail(self, role_id):
        """
        获取角色详情
        :param role_id: 角色Id
        :return: {
            'role':{
                'name':'财务',
                'groupId':1002
            },
            'errcode':0,
            'errmsg':'成功'
        }
        """

        extra_data = {'roleId': role_id}

        return self.request_manager.post(
            request_url=constants.ROLE_GET_ROLE_DETAIL,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def create_role(self, role_name, group_id):
        """
        创建角色
        :param role_name:String 角色名称
        :param group_id: Number 角色组id
        :return: {
            'roleId':1,
            'errcode': 0,
            'errmsg': 'ok'
        }
        """

        extra_data = {'roleName': role_name, 'groupId': group_id}

        return self.request_manager.post(
            request_url=constants.ROLE_CREATE_ROLE,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def update_role(self, role_name, role_id):
        """
        更新角色
        :param role_name: String 角色名称
        :param role_id: Number 角色id
        :return: {
            'errcode':0,
            'errmsg':'ok',
        }
        """

        extra_data = {
            'roleName': role_name,
            'roleId': role_id,
        }

        return self.request_manager.post(
            request_url=constants.ROLE_UPDATE_ROL,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def delete_role(self, role_id):
        """
         删除角色
        :param role_id: Number 角色ID
        :return:{
            'errcode':0,
            'errmsg':'ok',
        }
        """
        extra_data = {
            'role_id': role_id,
        }

        return self.request_manager.post(
            request_url=constants.ROLE_DELETE_ROLE,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def create_role_group(self, name):
        """
        创建角色组
        :param name:String 角色组名称
        :return:{
            'groupId':11,
            'errcode': 0,
            'errmsg': 'ok'
        }
        """

        extra_data = {'name': name}

        return self.request_manager.post(
            request_url=constants.ROLE_CREATE_ROLE_GROUP,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def add_users_roles(self, role_ids, user_ids):
        """
        批量添加员工到角色列表
        :param role_ids: String 1,2,3  角色id list，最大列表长度：20
        :param user_ids: String a,b,c 员工id list，最大列表长度：100
        :return: {
            'errcode':0,
            'errmsg':'成功'
        }
        """

        extra_data = {'roleIds': role_ids, 'userIds': user_ids}

        return self.request_manager.post(
            request_url=constants.ROLE_ADD_USERS_ROLES,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def delete_users_roles(self, role_ids, user_ids):
        """
        批量删除员工的角色
        :param role_ids: String 1,2,3  角色id list，最大列表长度：20
        :param user_ids: String a,b,c 员工id list，最大列表长度：100
        :return: {
            'errcode':0,
            'errmsg':'成功'
        }
        """

        extra_data = {'roleIds': role_ids, 'userIds': user_ids}

        return self.request_manager.post(
            request_url=constants.ROLE_DEL_USERS_ROLES,
            request_params={'access_token': self.token()},
            request_data=extra_data)

    def token(self):
        """
        get_access_token for short
        :return:access_token
        """
        return self.token_manager.get_access_token()
