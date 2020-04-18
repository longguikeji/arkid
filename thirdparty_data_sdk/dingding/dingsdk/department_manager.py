"""
Dingding department manage api
"""

from ....thirdparty_data_sdk.dingding.dingsdk import constants
from ....thirdparty_data_sdk.dingding.dingsdk.request_manager import RequestManager


class DepartmentManager():
    """
    Department Manage class, init with AccessTokenManager instance
    """
    def __init__(self, token_manager):
        """
        init the DepartmentManager
        :param AccessTokenManager token_manager: instance of AccessTokenManager
        """
        self.token_manager = token_manager
        self.request_manager = RequestManager()

    def get_subdep_listids(self, department_id):
        """
        获取直属子部门id列表
        :param department_id:stirng 部门id
        :return:{
            'errcode': 0,
            'errmsg': 'ok',
            'sub_dept_id_list': [ 2,3,4,5 ]
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_GET_SUB_DEP_LIST,
                                        request_params={
                                            'access_token': self.token(),
                                            'id': department_id
                                        })

    def list_parent_deps(self, department_id='1'):
        """
        假设部门的组织结构如下：
        1
          |->123
            |->456
              |->789
        当传入部门id为789时，返回的结果按顺序依次为当前部门id及其所有父部门的ID，直到根部门，如[789,456,123,1]
        :param department_id:string 部门id
        :return:{
            'errcode': 0,
            'errmsg': 'ok'，
            'parentIds':[789,456,123,1]
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_LIST_PARENT_DEPS,
                                        request_params={
                                            'access_token': self.token(),
                                            'id': department_id
                                        })

    def get_user_list_parentdeps(self, userid=''):
        """
        假设用户所属部门的组织结构如下
        1
          |->123
            |->456  ->员工A
          |->789  ->员工A
        当传入员工A的userId时，返回的结果按顺序依次为其所有父部门的ID，直到根部门，如[[456,123,1],[789,1]]。
        :param userid: 查询的用户id
        :return:{
            'errcode': 0,
            'errmsg': 'ok'，
            'department':[[456,123,1],[789,1]]
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_USER_LIST_PARENT_DEPS,
                                        request_params={
                                            'access_token': self.token(),
                                            'userId': userid
                                        })

    def get_users(self, department_id, offset, size, order='custom'):
        """
        获取部门下员工的详情，不递归
        :param: {
            department_id:long 获取的部门id
            offset:long 支持分页查询，与size参数同时设置时才生效，此参数代表偏移量
            size:int 支持分页查询，与offset参数同时设置时才生效，此参数代表分页大小，最大100
            order:支持分页查询，部门成员的排序规则，默认不传是按自定义排序；
            entry_asc：代表按照进入部门的时间升序，
            entry_desc：代表按照进入部门的时间降序，
            modify_asc：代表按照部门信息修改时间升序，
            modify_desc：代表按照部门信息修改时间降序，
            custom：代表用户定义(未定义时按照拼音)排序
        }
        :returns: {
            'errcode': 0,
            'errmsg': 'ok',
            'hasMore': False,
            'userlist':[
                {
                    'userid': 'zhangsan',
                    'dingId': 'dwdded',
                    'mobile': '13122222222',
                    'tel' : '010-123333',
                    'workPlace' :'',
                    'remark' : '',
                    'order' : 1,
                    'isAdmin': True,
                    'isBoss': False,
                    'isHide': True,
                    'isLeader': True,
                    'name': '张三',
                    'active': True,
                    'department': [1, 2],
                    'position': '工程师',
                    'email': 'zhangsan@alibaba-inc.com',
                    'avatar':  './dingtalk/abc.jpg',
                    'jobnumber': '111111',
                    'extattr': {
                        '爱好':'旅游',
                        '年龄':'24'
                    }
                }
            ]
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_GET_USERS_URL,
                                        request_params={
                                            'access_token': self.token(),
                                            'department_id': department_id,
                                            'offset': offset,
                                            'size': size,
                                            'order': order,
                                        })

    def get_users_brief(self, department_id, offset, size, order='custom'):
        """
        获取部门下员工的userid，name的list，不递归
        :param: {
            department_id:long 获取的部门id
            offset:long 支持分页查询，与size参数同时设置时才生效，此参数代表偏移量
            size:int 支持分页查询，与offset参数同时设置时才生效，此参数代表分页大小，最大100
            order:支持分页查询，部门成员的排序规则，默认不传是按自定义排序；
            entry_asc：代表按照进入部门的时间升序，
            entry_desc：代表按照进入部门的时间降序，
            modify_asc：代表按照部门信息修改时间升序，
            modify_desc：代表按照部门信息修改时间降序，
            custom：代表用户定义(未定义时按照拼音)排序
        }
        :returns: {
            'errcode': 0,
            'errmsg': 'ok',
            'hasMore': False,
            'userlist': [
                {
                    'userid': 'manager8659',
                    'name': '张三'
                }, {
                    'userid': 'zhangsan1',
                    'name': '张三'
                }
            ],
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_USER_SIMPLELIST_URL,
                                        request_params={
                                            'access_token': self.token(),
                                            'department_id': department_id,
                                            'offset': offset,
                                            'size': size,
                                            'order': order,
                                        })

    def get_subdep_list(self, department_id, fetch_child=True):
        """
        获取子部门列表
        :param department_id:string 部门id
        :param fetch_child: 是否递归子部门
        :return:{
            'errcode': 0,
            'errmsg': 'ok',
            'department': [
                {
                    'id': 2,
                    'name': '钉钉事业部',
                    'parentid': 1,
                    'createDeptGroup': true,
                    'autoAddUser': true
                },{
                    'id': 3,
                    'name': '服务端开发组',
                    'parentid': 2,
                    'createDeptGroup': false,
                    'autoAddUser': false
                }
            ]
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_GET_DEP_LIST,
                                        request_params={
                                            'access_token': self.token(),
                                            'id': department_id,
                                            'fetch_child': fetch_child,
                                        })

    def get_dep_detail(self, department_id):
        """
        获取部门详情
        :param department_id:string 部门id
        :return: {
            'errcode': 0,
            'errmsg': 'ok',
            'id': 2,
            'name': '钉钉事业部',
            'order' : 10,
            'parentid': 1,
            'createDeptGroup': true,
            'autoAddUser': true,
            'deptHiding' : true,
            'deptPermits' : '3|4',
            'userPermits' : 'userid1|userid2',
            'outerDept' : true,
            'outerPermitDepts' : '1|2',
            'outerPermitUsers' : 'userid3|userid4',
            'orgDeptOwner' : 'manager1122',
            'deptManagerUseridList' : 'manager1122|manager3211',
            'sourceIdentifier' : 'source'
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_GET_DETAIL,
                                        request_params={
                                            'access_token': self.token(),
                                            'id': department_id,
                                        })

    def create_dep(self, parent_id, name, **kwargs):
        """
        创建部门
        :param parent_id:父部门id
        :param name: 部门名称
        :param kwargs:{
            'order': '1',
            'createDeptGroup': true,
            'deptHiding' : true,
            'deptPermits' : '3|4',
            'userPermits' : 'userid1|userid2',
            'outerDept' : true,
            'outerPermitDepts' : '1|2',
            'outerPermitUsers' : 'userid3|userid4',
            'sourceIdentifier' : 'source'
        }
        :return:{
            'errcode': 0,
            'errmsg': 'created',
            'id': 2
        }
        """

        createdata = {
            'name': name,
            'parentid': parent_id,
        }
        createdata.update(kwargs)

        return self.request_manager.post(
            request_url=constants.DEPARTMENT_CREATE_DEP,
            request_params={'access_token': self.token()},
            request_data=createdata,
        )

    def update_dep(self, department_id, **kwargs):
        """
        更新部门信息
        :param department_id: string 部门id
        :param kwargs:{
            'name': '钉钉事业部',
            'parentid': '1',
            'order': '1',
            'id': 1,
            'createDeptGroup': true,#是否创建一个关联此部门的企业群
            'autoAddUser': true,#如果有新人加入部门是否会自动加入部门群
            'deptManagerUseridList': 'manager1111|2222',
            'deptHiding' : true,
            'deptPermits' : '3|4',
            'userPermits' : 'userid1|userid2',
            'outerDept' : true,
            'outerPermitDepts' : '1|2',
            'outerPermitUsers' : 'userid3|userid4',
            'orgDeptOwner': 'manager1111',
            'sourceIdentifier' : 'source'
        }
        :return:{
            'errcode': 0,
            'errmsg': 'ok',
            'id': 61602002 #更新后的部门id

        }
        """

        updatedata = {
            'id': department_id,
        }
        updatedata.update(kwargs)

        return self.request_manager.post(
            request_url=constants.DEPARTMENT_UPDATE_DEP,
            request_params={'access_token': self.token()},
            request_data=updatedata,
        )

    def delete_dep(self, department_id):
        """
        删除部门
        :param department_id:string 部门id(注：不能删除根部门；不能删除含有子部门、成员的部门)
        :return:{
            'errcode': 0,
            'errmsg': 'ok'
        }
        """

        return self.request_manager.get(request_url=constants.DEPARTMENT_DEL_DEP,
                                        request_params={
                                            'access_token': self.token(),
                                            'id': department_id
                                        })

    def token(self):
        """
        get_access_token for short
        :return:access_token
        """
        return self.token_manager.get_access_token()
