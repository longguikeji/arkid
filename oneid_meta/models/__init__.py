'''
schema of Users,Departmments,Groups,Perms
'''
#pylinit: disable=cyclic-import

from oneid_meta.models.user import (User, PosixUser, CustomUser, DingUser, AlipayUser,\
    WorkWechatUser, WechatUser, QQUser, SubAccount)

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

from oneid_meta.models.org import (
    Org,
    OrgMember,
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

from oneid_meta.models.appgroup import (
    AppGroup, )

from oneid_meta.models.config import (CompanyConfig, AccountConfig, SMSConfig, DingConfig, CustomField, NativeField,
                                      EmailConfig, AlipayConfig, WorkWechatConfig, WechatConfig, QQConfig,
                                      StorageConfig, MinioConfig)

from oneid_meta.models.event import (
    Invitation, )

from oneid_meta.models.log import (
    Log,
    RequestAccessLog,
    RequestDataClientLog,
)
