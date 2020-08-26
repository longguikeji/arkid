'''
schema of Users,Departmments,Groups,Perms
'''

from oneid_meta.models.user import (User, PosixUser, CustomUser, DingUser, AlipayUser,\
    WorkWechatUser, WechatUser, QQUser, SubAccount, AliyunSSORole, GithubUser)

from oneid_meta.models.dept import (
    Dept,
    DingDept,
    DeptMember,
)

from oneid_meta.models.group import (
    Group,
    DingGroup,
    ManagerGroup,
    GroupMember,
)

from oneid_meta.models.perm import (
    Perm,
    GroupPerm,
    DeptPerm,
    UserPerm,
)

from oneid_meta.models.app import (
    APP,
    OAuthAPP,
    OIDCAPP,
    SAMLAPP,
    LDAPAPP,
    HTTPAPP,
)

# pylint: disable=line-too-long
from oneid_meta.models.config import (CompanyConfig, AccountConfig, SMSConfig, DingConfig, CustomField, NativeField,
                                      EmailConfig, AlipayConfig, WorkWechatConfig, WechatConfig, QQConfig,
                                      StorageConfig, MinioConfig, PasswordComplexityConfig, I18NMobileConfig,
                                      GithubConfig)

from oneid_meta.models.event import (
    Invitation, )

from oneid_meta.models.log import (
    Log,
    RequestAccessLog,
    RequestDataClientLog,
)

from oneid_meta.models.advance import (
    MiddlewarePlugin,
    CrontabPlugin,
)
