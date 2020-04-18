"""
Dingding user manage api
"""

from ....thirdparty_data_sdk.dingding.dingsdk import constants
from ....thirdparty_data_sdk.dingding.dingsdk.request_manager import RequestManager


class UserManager():
    """
    User Manage class, init with AccessTokenManager instance
    """
    def __init__(self, token_manager):
        """
        init the UserManager
        :param AccessTokenManager token_manager: instance of AccessTokenManager
        """
        self.token_manager = token_manager
        self.request_manager = RequestManager()

    def get_user_count(self, onlyactive=False):
        """
        获取企业员工人数
        :param:onlyActive:False：包含未激活钉钉的人员数量 True：不包含未激活钉钉的人员数量
        :return:{
            'count': 6,
            'errcode': 0,
            'errmsg': 'ok'
        }
        """

        onlyactive_opt = 1 if onlyactive else 0
        return self.request_manager.get(request_url=constants.USER_GET_USER_COUNT_URL,
                                        request_params={
                                            'access_token': self.token(),
                                            'onlyActive': onlyactive_opt
                                        })

    def add_user(self, name, mobile, departments, **kwargs):
        """
        :param str name: 成员名称。长度为1~64个字符
        :param str mobile: 手机号码。企业内必须唯一
        :param [int] departments: 成员所属部门id列表
        :returns: {
            'errcode': 0,
            'errmsg': 'created',
            'userid': 'zhangsan'
        }
        """

        userdata = {
            'name': name,
            'mobile': mobile,
            'department': departments,
        }
        userdata.update(kwargs)

        return self.request_manager.post(
            request_url=constants.USER_CREATE_URL,
            request_params={'access_token': self.token()},
            request_data=userdata,
        )

    def delete_user(self, uid):
        """
        :param str uid: 员工唯一标识
        :returns{
            'errcode': 0,
            'errmsg': 'deleted'
        }
        """

        return self.request_manager.get(request_url=constants.USER_DELETE_URL,
                                        request_params={
                                            'access_token': self.token(),
                                            'userid': uid
                                        })

    def update_user(self, uid, **kwargs):
        """
        如果非必须的字段未指定，则钉钉后台不改变该字段之前设置好的值
        :param uid: 员工唯一标识
        :param kwargs: 需要更新的参数列表
        {
            'userid': 'zhangsan',
            'name': '张三',
            'department': [1, 2],
            'orderInDepts': '{1:10}',
            'position': '产品经理',
            'mobile': '15913215421',
            'tel': '010-123333',
            'workPlace':'',
            'remark': '',
            'email': 'zhangsan@gzdev.com',
            'orgEmail': 'qiye@gzdev.com',
            'jobnumber': '111111',
            'isHide': false,
            'isSenior': false,
            'extattr': {
                '爱好':'旅游',
                '年龄':'24'
            }
        }
        :return:{
            'errcode': 0,
            'errmsg': 'updated'
        }
        """

        userdata = {
            'userid': uid,
        }
        userdata.update(kwargs)

        return self.request_manager.post(
            request_url=constants.USER_UPDATE_URL,
            request_params={'access_token': self.token()},
            request_data=userdata,
        )

    def get_user_detail(self, uid):
        """
        :param str uid: 员工唯一标识
        :returns: {
            'errcode': 0,
            'errmsg': 'ok',
            'userid': 'zhangsan',
            'name': '张三',
            'tel': '010-123333',
            'workPlace' :'',
            'remark': '',
            'mobile': '13800000000',
            'email': 'dingding@aliyun.com',
            'active': true,
            'orderInDepts': '{1:10, 2:20}',
            'isAdmin': false,
            'isBoss': false,
            'openId': 'WsUDaq7DCVIHc6z1GAsYDSA',
            'unionid': 'cdInjDaq78sHYHc6z1gsz',
            'isLeaderInDepts' : '{1:true, 2:false}',
            'isHide': false,
            'department': [1, 2],
            'position': '工程师',#职位信息
            'avatar': 'dingtalk.com/abc.jpg',
            'jobnumber': '111111',
            'isSenior': False,
            'stateCode': '86',
            'id': 394299625,
            'roles': [{u'groupName': '岗位', 'type': 0, 'id': 394299625, 'name': '经理'}],
        }
        """

        return self.request_manager.get(request_url=constants.USER_GET_DETAIL_URL,
                                        request_params={
                                            'access_token': self.token(),
                                            'userid': uid
                                        })

    def token(self):
        """
        get_access_token for short
        :return:access_token
        """
        return self.token_manager.get_access_token()
