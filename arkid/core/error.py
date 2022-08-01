from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    OK = '0'
    # USERNAME_PASSWORD_MISMATCH = '10001-1'
    # PASSWORD_NONE_ERROR = '10001-2'
    # PASSWORD_STRENGTH_ERROR = '10001-3'
    # PASSWORD_CONFIRM_ERROR = '10001-4'
    
    # SMS_CODE_MISMATCH = '10002'
    # EMAIL_CODE_MISMATCH = '10021'
    # USERNAME_EXISTS_ERROR = '10004'


    # TENANT_NO_ACCESS = '10003'
    # TENANT_NO_EXISTS = '10007'
    # CODE_EXISTS_ERROR = '10008'
    # CODE_FILENAME_EXISTS_ERROR = '10009'
    # AUTHCODE_ERROR = '10010'
    # OLD_PASSWORD_ERROR = '10011'
    # USER_EXISTS_ERROR = '10012'
    # SLUG_EXISTS_ERROR = '10013'
    # REGISTER_FAST_ERROR = '10014'
    # URI_FROMAT_ERROR = '10015'
    # FILE_FROMAT_ERROR = '10016'
    # DATA_PATH_ERROR = '10017'
    # EMAIL_FROMAT_ERROR = '10018'
    # MOBILE_FROMAT_ERROR = '10019'
    # PASSWORD_CHECK_ERROR = '10020'
    # MOBILE_NOT_EXISTS_ERROR = '10021'
    # MOBILE_EXISTS_ERROR = '10022'
    # EMAIL_NOT_EXISTS_ERROR = '10023'
    # EMAIL_EXISTS_ERROR = '10024'
    # QUERY_PARAM_ERROR = '10025'
    # DUPLICATED_RECORD_ERROR = '10026'
    # POST_DATA_ERROR = '10027'
    # PROVIDER_NOT_EXISTS_ERROR = '10028'
    # PASSWORD_EXPIRED_ERROR = '10029'
    # USER_NOT_IN_TENANT_ERROR = '10030'
    PERMISSION_EXISTS_ERROR = ('10033', _('the permission not exists', '该权限不存在'))
    
    # APP_EXISTS_ERROR = '10032'
    PERMISSION_NOT_EDIT = ('10033', _('the permission not edit', '该权限不允许编辑'))
    PERMISSION_NOT_CLOSE = ('10033', _('the permission not edit', '该权限不允许关闭'))
    # PERMISSION_NOT_DELETE = ('10034', _('the permission not delete', '该权限不允许删除'))
    BAN_REMOVE_GROUP_PERMISSION = ('10035', _('ban remove group permission', '该分组权限或范围不允许移除'))
    BAN_REMOVE_GROUP_SCOPE = ('10036', _('ban remove group permission', '该分组范围不允许移除'))
    PERMISSION_GROUP_NOT_EDIT = ('10037', _('the permission group not edit', '该分组权限不允许编辑'))
    PERMISSION_GROUP_NOT_DELETE = ('10038', _('the permission group not delete', '该分组权限不允许删除'))
    SYSTEM_PERMISSION_NOT_OPERATION = ('10033', _('system permission not operation', '系统权限不支持此操作'))

    # SMS_PROVIDER_IS_MISSING = '11001'
    # AUTHCODE_PROVIDER_IS_MISSING = '11002'
    # LOCAL_STORAGE_PROVIDER_IS_MISSING = '11003'

    # USER_IMPORT_ERROR = '12001'
    # GROUP_IMPORT_ERROR = '12002'
    # MOBILE_ERROR = '12003'
    # EMAIL_ERROR = '12004'

    # ADD_AUTH_TMPL_ERROR = '13001'

    APPROVE_ACTION_DUPLICATED = ('14001', _('approve action duplicated', '审批动作重复'))
    APPROVE_ACTION_NOT_EXISTS = ('14002', _('approve action not exists', '审批动作不存在'))
    APPROVE_REQUEST_WAITING = ('14003', _('approve request created, please wait', '审批请求已创建，等待审批'))

    WEBHOOK_NOT_EXISTS = ('15001', _('webhook not exists', '回调动作不存在'))
    WEBHOOK_HISTORY_NOT_EXISTS = ('15002', _('webhook history not exists', '回调动作历史不存在'))
    
    APP_GROUP_PARENT_CANT_BE_ITSELF = ('16001', _('app group parent can not be itself', '应用分组上级分组不能设置为其自身'))
    USER_GROUP_PARENT_CANT_BE_ITSELF = ('16002', _('user group parent can not be itself', '用户分组上级分组不能设置为其自身'))

    RENT_EXTENSION_SUCCESS = ('17001', _('rent extension success', '插件租赁成功'))
    UPDATE_EXTENSION_SUCCESS = ('17002', _('extension not in arkstore', '插件不在插件商店中，无法更新'))
    TRIAL_EXTENSION_TWICE = ('17003', _('extension can not trial twice', '试用不允许重复下单'))
    AGENT_BIND_CAN_NOT_CHANGE = ('17004', _('agent bind can not change', '代理商已绑定，无法修改'))
    PLUG_IN_NOT_HIRE = ('17005', _('plug-in not hire', '插件没有租赁，无法使用'))
    
    PASSWORD_NOT_CORRECT = ('18001', _('password not correct', '密码不正确'))

    STORAGE_NOT_EXISTS = ('18002', _('storage not exists', '存储插件未启用'))
    STORAGE_FAILED = ('18003', _('storage failed', '存储失败'))
    
class ErrorDict(dict):

  def __init__(self, enum, package='core', **kwargs):
    if type(enum.value) is tuple:
      self['error'] = enum.value[0]
    else:
      self['error'] = enum.value
    
    if len(enum.value) > 1:
      message = enum.value[1]
      for key, value in kwargs.items():
        message.replace('{'+key+'}', value)
      self['message'] = message
    self['package'] = package
    
class SuccessDict(ErrorDict):
  def __init__(self, data = None, package='core', **kwargs):
    super().__init__(ErrorCode.OK, package, **kwargs)
    if data:
      self['data'] = data