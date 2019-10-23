"""
Dingding operation URL
"""

# token related value
TOKEN_DURATION = 7200
TOKEN_TOLERANCE_PERIOD = 5    #提前一定秒数更新token,防止临界点的访问
TOKEN_FROM_CORPID_CORPSECRET = 1
TOKEN_FROM_APPKEY_APPSECRET = 2
TOKEN_FROM_APPID_QR_APP_SECRET = 3

API_URL = 'https://oapi.dingtalk.com'

ACCESS_TOKEN_URL = API_URL + '/gettoken'

# usr operation url
USER_CREATE_URL = API_URL + '/user/create'
USER_DELETE_URL = API_URL + '/user/delete'
USER_UPDATE_URL = API_URL + '/user/update'
USER_GET_DETAIL_URL = API_URL + '/user/get'
USER_GET_USER_COUNT_URL = API_URL + '/user/get_org_user_count'

# department related url
DEPARTMENT_USER_SIMPLELIST_URL = API_URL + '/user/simplelist'
DEPARTMENT_GET_USERS_URL = API_URL + '/user/listbypage'
DEPARTMENT_GET_DEP_LIST = API_URL + '/department/list'
DEPARTMENT_GET_DETAIL = API_URL + '/department/get'
DEPARTMENT_CREATE_DEP = API_URL + '/department/create'
DEPARTMENT_UPDATE_DEP = API_URL + '/department/update'
DEPARTMENT_DEL_DEP = API_URL + '/department/delete'
DEPARTMENT_GET_SUB_DEP_LIST = API_URL + '/department/list_ids'
DEPARTMENT_LIST_PARENT_DEPS = API_URL + '/department/list_parent_depts_by_dept'
DEPARTMENT_USER_LIST_PARENT_DEPS = API_URL + '/department/list_parent_depts'

# role related url
ROLE_GET_ROLES_LIST = API_URL + '/topapi/role/list'
ROLE_GET_ROLE_USERLIST = API_URL + '/topapi/role/simplelist'
ROLE_GET_ROLE_GROUP = API_URL + '/topapi/role/getrolegroup'
ROLE_GET_ROLE_DETAIL = API_URL + '/topapi/role/getrole'
ROLE_CREATE_ROLE = API_URL + '/role/add_role'

ROLE_UPDATE_ROL = API_URL + '/role/update_role'
ROLE_DELETE_ROLE = API_URL + '/topapi/role/deleterole'
ROLE_CREATE_ROLE_GROUP = API_URL + '/role/add_role_group'
ROLE_ADD_USERS_ROLES = API_URL + '/role/addrolesforemps'
ROLE_DEL_USERS_ROLES = API_URL + '/role/removerolesforemps'

# message related url
MSG_SEND_URL = API_URL + '/topapi/message/corpconversation/asyncsend_v2'
MSG_GET_SEND_PROGRESS_URL = API_URL + '/topapi/message/corpconversation/getsendprogress'
MSG_GET_SEND_RESULT_URL = API_URL + '/topapi/message/corpconversation/getsendresult'

# id related
DING_ID_FROM_CODE = 1

# qr related url
QR_BASEURL = 'https://oapi.dingtalk.com/sns/'
QR_GET_ACCESS_TOKEN_URL = QR_BASEURL + 'gettoken'
QR_GET_PSSTT_CODE_URL = QR_BASEURL + 'get_persistent_code'
QR_GET_SNS_TOKEN_URL = QR_BASEURL + 'get_sns_token'
QR_GET_USER_INFO_URL = QR_BASEURL + 'getuserinfo'
