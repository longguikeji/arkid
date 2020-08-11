FORMAT: 1A

# OneID
|Q|A|
|----|----|
|namespace|/siteapi/v1/|
|docs|/siteapi/v1/docs/|
|token|以`HTTP_AUTHORIZATION`: `Token {%token%}` 形式置于请求头中|

# Data Structures
## UserLite (object)
+ user_id (number)
+ username (string)
+ name (string)

## CustomUser (object)
+ data (object) - key为字段uuid
+ pretty (array) - read only
    + item (object)
        + name (string) - 字段名称
        + uuid (string) - 字段uuid
        + value (string) - 值

## WechatUser (object)
+ unionid (string)

## GithubUser (object)
+ github_user_id (string)

## UserProfile (object)
+ username (string)
+ name (string)
+ email (string)
+ mobile (string)
+ avatar (string)
+ number (string) - 工号
+ private_email (string) - 私人邮箱
+ position (string) - 职位
+ remark (string) - 备注
+ depts (array) - 所属部门列表
    + dept (object)
        + uid (string)
        + name (string)
+ gender (enum[number])
    + 1 - 男
    + 2 - 女
+ custom_user (CustomUser) - May Null-> 无该键
+ visible_fields (array[string]) - 由key构成，按需使用

## User(object)
+ uuid (string)
+ user_id (number)
+ username (string)
+ name (string)
+ email (string)
+ mobile (string)
+ avatar (string)
+ number (string) - 工号
+ private_email (string) - 私人邮箱
+ position (string) - 职位
+ is_settled (boolean) - 是否已入驻
+ is_manager (boolean) - 是否是子管理员
+ is_admin (boolean) - 是否是超级管理员
+ is_extern_user (boolean) - 是否是外部用户
+ origin_verbose (string) - 注册来源
+ remark (string) - 备注
+ hiredate (string) - 入职时间 2019-06-04T09:01:44+08:00
+ created (string) - 创建时间、注册时间 2019-06-04T09:01:44+08:00
+ last_active_time (string) - 最后活跃时间
+ gender (enum[number])
    + 1 - 男
    + 2 - 女
+ ding_user (object) - May Null-> 无该键
    + uid (string, optional)
    + account (string, required) - 关联mobile
    + data (string) - json
        + name (string, required) - 关联username
        + position (string, optional) - 职位信息
        + tel (string, optional) - 分机号
        + workPlace (string, optional) - 办公地点
        + remark (string, optional)
        + email (string, optional)
        + orgEmail (string, optional) - 企业邮箱
        + jobnumber (string, optional) - 员工工号
        + isHide (string, optional) - 是否隐藏手机号
        + isSenior (string, optional) - 是否高管模式
+ posix_user (object) - May Null-> 无该键
    + uid
    + gid
    + home
    + pub_key
+ custom_user (CustomUser) - May Null-> 无该键
+ wechat_user (WechatUser)
+ github_user (GithubUser) - github关联用户
+ require_reset_password(boolean) - 是否需要重置密码
+ has_password (boolean) - 是否有密码，目前仅用于邀请链接的页面

## CreateUser(User)
+ password (string) - 密码，明文

## UserWithPerm(User)
+ perms (array[string]) - 拥有授权的权限的uid
+ roles (array[string]) - 特殊角色，admin, manager等

## UserWithPermWithToken(UserWithPerm)
+ token (string)

## Employee(User)
+ nodes (array[Node])

## SubAccount(object)
+ domain (string)
+ username (string)
+ password (string)

## Group
+ group_id (number)
+ uid (string)
+ node_subject (string) - 节点类型，提示角色、标签等
+ name (string)
+ remark (string)
+ accept_user (boolean) - 是否接纳人员，对于角色组为否
+ ding_group (DingGroup) - 钉钉组信息
+ manager_group (ManagerGroup) - 子管理员组信息

## DingGroup (object)
+ uid (number) from Ding
+ data (string) - json
+ subject (enum[string])
    + role - 角色，内部人员
    + label - 标签，外部人员
+ is_group (boolean) - 区分角色与角色组、标签与标签组

## ManagerGroup (object)
+ nodes (array[string]) - list of node_uids, 管理范围指定节点列表
+ users (array[string]) - list of username, 管理范围指定人员列表
+ apps (array[string]) - list of app.uid, 管理范围指定应用列表
+ perms (array[string]) - list of system perm.uid, 管理范围系统权限列表
+ scope_subject (enum[number]) - 管理范围类型
    + 1 - 所在节点及其下属子孙节点
    + 2 - 指定节点和人员，只有选择该项，`nodes`，`users` 才生效

## VerboseManagerGroup (ManagerGroup)
+ nodes (array)
    + node (object)
        + node_uid
        + name
        + node_subject
+ users (array)
    + user (object)
        + username
        + name
+ apps (array)
    + app (object)
        + uid
        + name
+ perms (array)
    + perm (object)
        + uid
        + name


## GroupWithParent (Group)
+ parent_uid (string)
+ parent_name (string)

## GroupDetail (GroupWithParent)
+ visibility (enum[number]) - 可见范围类型
    + 1 - 所有人可见
    + 2 - 节点成员可见
    + 3 - 节点成员及其下属节点均可见
    + 4 - 只对指定人、节点可见
    + 5 - 所有人不可见
+ node_scope (array[string]) - 特定可见节点范围，仅当 visibility=4 时生效，下同
+ user_scope (array[string]) - 特定可见用户范围

## GroupTree (object)
+ info (Group)
+ users (array[UserLite])
+ groups (array[GroupTree]) - self
+ headcount (number) - 该组及其子孙部门人数之和

## GroupOnlyTree (object)
+ info (Group)
+ groups (array[GroupOnlyTree]) - self

## Dept (object)
+ dept_id (number)
+ uid (string)
+ node_subject (string) - 节点类型，恒为`dept`
+ name (string)
+ remark (string)
+ ding_dept (DingDept) - 钉钉部门信息 May Null-> 无该键


## DingDept (object)
+ uid (string, optional)
+ data (string) - json
    + order (string, optional)
    + createDeptGroup (boolean, optional)
    + deptHiding (boolean, opational)
    + depPermits (string, optional) - 可以查看指定隐藏部门的其他部门列表, '\|'分隔
    + userPermits (string) - 可以查看指定隐藏部门的其他人员列表, '\|'分隔
    + outerDept (boolean, optional) - 限制本部门成员查看通讯录，本部门成员只能看到限定范围内的通讯录。true表示限制开启
    + outerPermitDepts (string, optional) - 配置额外可见部门，值为部门id组成的的字符串，使用“\|”符号进行分割
    + outerPermitUsers (string, optional) - 配置额外可见人员，值为userid组成的的字符串，使用“\|”符号进行分割
    + outerDeptOnlySelf (boolean, optional) - 为true时，表示只能看到所在部门及下级部门通讯录
    + sourceIdentifier (string, optional) - 部门标识字段，开发者可用该字段来唯一标识一个部门，并与钉钉外部通讯录里的部门做映射


## DeptWithParent (Dept):
+ parent_uid (string)
+ parent_name (string)

## DeptDetail (Dept)
+ visibility (enum[number]) - 可见范围类型
    + 1 - 所有人可见
    + 2 - 节点成员可见
    + 3 - 节点成员及其下属节点均可见
    + 4 - 只对指定人、节点可见
    + 5 - 所有人不可见
+ node_scope (array[string]) - 特定可见节点范围，仅当 visibility=4 时生效，下同
+ user_scope (array[string]) - 特定可见用户范围

## DeptTree (object)
+ info (Dept)
+ users (array[UserLite])
+ depts (array[DeptTree]) - self
+ headcount (number) - 该部门及其子孙部门人数之和

## DeptOnlyTree (object)
+ info (Dept)
+ depts (array[DeptOnlyTree]) - self

## Node (object)
+ node_uid (string) - 在部门和组范围内唯一
+ node_subject (string) - 节点类型，提示角色、标签等
+ name (string)
+ remark (string)
+ ding_group (DingGroup) - 钉钉组信息
+ ding_dept(DingDept) - 钉钉部门信息
+ manager_group(ManagerGroup) - 子管理员组信息

## NodeWithParent (Node)
+ parent_node_uid (string)
+ parent_name (string)

## NodeDetail (NodeWithParent)
+ visibility (enum[number]) - 可见范围类型
    + 1 - 所有人可见
    + 2 - 节点成员可见
    + 3 - 节点成员及其下属节点均可见
    + 4 - 只对指定人、节点可见
    + 5 - 所有人不可见
+ node_scope (array[string]) - 特定可见节点范围，仅当 visibility=4 时生效，下同
+ user_scope (array[string]) - 特定可见用户范围

## NodeTree (object)
+ info (Node)
+ users (array[UserLite])
+ nodes (array[NodeTree]) - self
+ headcount (number) - 该部门及其子孙部门人数之和

## NodeOnlyTree (object)
+ info (Node)
+ nodes (array[NodeOnlyTree]) - self

## Perm (object)
+ perm_id (number)
+ uid (string)
+ name
+ remark
+ scope
+ action
+ subject
+ sub_account (SubAccount, optional)

## PermWithOwner(Perm)
+ permit_owners (object) - 白名单部分内容
    + count (number) - 总数
    + has_more (boolean) - 如果还有更多，请调用专门的接口获取 权限拥有者 列表
    + results (array)
        + owner (object)
            + uid (string)
            + name (string)
            + subject (string)
+ reject_owners (object) - 黑名单部分内容
    + count (number) - 总数
    + has_more (boolean) - 如果还有更多，请调用专门的接口获取 权限拥有者 列表
    + results (array)
        + owner (object)
            + uid (string)
            + name (string)
            + subject (string)

## PermResult (object)
+ perm (Perm)
+ status (enum[number])
    - -1 - 显式拒绝
    - 0 - 随上级决定
    - 1 - 显式授权
+ value (boolean) - 有无权限。该字段为最终判断依据
+ locked (boolean) - 是否可编辑，True：不可编辑

## UserPerm (object)
+ perm (Perm)
+ status (enum[number])
    - -1 - 显式拒绝
    - 0 - 随上级决定
    - 1 - 显式授权
+ dept_perm_value (boolean)
+ group_perm_value (boolean)
+ node_perm_value (boolean) - 分组权限判定结果
+ value (boolean) - 有无权限。该字段为最终判断依据

## UserPermDetail (UserPerm)
+ source (array)
    + item (object)
        + name (string)
        + uid (string)
        + node_uid (string)
        + node_subject (string)

## PublicAPP(object)
+ uid (string)
+ name (string)
+ remark (string)
+ auth_protocols (array[string])
+ logo (string) - file key
+ index (string) - 首页地址

## APP (object)
+ uid (string)
+ uuid (string)
+ name (string)
+ remark (string)
+ oauth_app (OAuthAPP)
+ ldap_app (LDAPAPP)
+ http_app (HTTPAPP)
+ saml_app (SAMLAPP)
+ auth_protocols (array[string])
+ logo (string) - file key
+ index (string) - 首页地址

## APPWithAccess (APP)
+ access_perm (PermWithOwner) - 登录权限
+ access_result (object)
    + node_uid (string) - 查询参数，该节点有无该APP访问权限
    + user_uid (string) - 查询参数，该用户有无该APP访问权限
    + value (boolean) - 是否有访问权限

## OAuthAPP (object)
+ client_id (string) - 自动生成
+ client_secret (string) - 自动生成
+ redirect_uris (string, required)
+ client_type (enum[string])
    - confidential - default
    - public 
+ authorization_grant_type (enum[string])
    - authorization-code - default
    - implicit
    - password
    - client-credentials
+ more_detail (array)
    + field (object)
        + name (string) - 字段名称，用于显示
        + key (string) - 键
        + value (string) - 值，用于显示

## LDAPAPP (object)
+ more_detail (array)
    + field (object)
        + name (string) - 字段名称，用于显示
        + key (string) - 键
        + value (string) - 值，用于显示

## HTTPAPP (object)
+ more_detail (array)
    + field (object)
        + name (string) - 字段名称，用于显示
        + key (string) - 键
        + value (string) - 值，用于显示

## SAMLAPP (object)
+ app (object) - OnetoOne关联APP对象
+ entity_id (string) - SP方SAML实体
+ acs (string) - SP单点登录uri
+ sls (string) - SP单点登出uri
+ cert (string) - SP公钥证书
+ xmldata (string) - SP方xml元数据文件

## CompanyConfig (object)
+ name_cn (string)
+ fullname_cn (string)
+ name_en (string)
+ fullname_en (string)
+ icon (string)
+ address (string)
+ domain (string)
+ color (string)


## AccountConfig (object)
+ allow_register (boolean) - 是否允许账号注册
+ allow_mobile (boolean) - 是否允许手机号登录
+ allow_email (boolean) - 是否允许邮箱登录
+ allow_ding_qr (boolean) - 是否允许钉钉扫码登录
+ allow_github (boolean) - 是否允许github账号登录

## SMSConfig (object)
+ vendor (string)
+ access_key (string)
+ access_secret (string) - write_only
+ signature (string) - 签名
+ template_code (string) - 通用短信模板ID
+ template_register (string) - 注册用短信模板ID
+ template_reset_pwd (string) - 重置密码用短信模板ID
+ template_activate （string) - 激活用短信模板ID
+ template_reset_mobile (string) - 重置手机用短信模板ID
+ template_login (string) - 登陆用短信模板ID
+ signature_i18n (string) - 国际-签名
+ template_code_i18n (string) - 国际-通用短信模板ID
+ template_register_i18n (string) - 国际-注册用短信模板ID
+ template_reset_pwd_i18n (string) - 国际-重置密码用短信模板ID
+ template_activate_i18n （string) - 国际-激活用短信模板ID
+ template_reset_mobile_i18n (string) - 国际-重置手机用短信模板ID
+ template_login_i18n (string) - 国际-登陆用短信模板ID
+ is_valid (boolean) - 是否有效

## EmailConfig (object)
+ host (string) - 邮件服务地址
+ port (number) - 邮件服务端口
+ access_key (string) - 邮箱账号
+ access_secret (string) - 邮箱密钥，- write_only
+ is_valid (boolean) - 是否有效

## DingConfig (object)
+ app_key (string)
+ app_secret (string) - write_only
+ app_valid (boolean, readonly) - app配置是否有效
+ corp_id (string)
+ corp_secret (string) - write_only
+ corp_valid (boolean, readonly) - corp配置是否有效
+ qr_app_id (string) - 扫码登录应用查询钉钉用户所需的id
+ qr_app_secret (string) - 原来也叫app_secret，为了与上面的区分所以加qr，是查询用户钉钉信息所需的secret
+ qr_app_valid (boolean, readonly) - qr配置是否有效

## AlipayConfig (object)
+ app_id (string)
+ app_private_key (string) - 网页应用私钥
+ alipay_public_key (string) - 支付宝生成的公钥
+ qr_app_valid (boolean, readonly) - qr配置是否有效

## PasswordComplexityConfig (object)
+ min_length (number) - 最小长度
+ min_upper (number) - 大写字母限制
+ min_lower (number) - 小写字母限制
+ min_letter (number) - 字母限制
+ min_digit (number) - 数字限制
+ min_special (number) - 特殊字符限制
+ min_word (number) - 单词限制
+ is_active (boolean) - 配置是否启用

## GithubConfig (object)
+ client_id (string) - github侧oauth应用唯一标识
+ client_secret (string) - github侧oauth应用秘钥
+ client_valid (boolean) - github侧oauth应用配置是否有效

## Config (object)
+ company_config (CompanyConfig)
+ ding_config (DingConfig)
+ account_config (AccountConfig)
+ sms_config (SMSConfig)
+ email_config (EmailConfig)
+ alipay_config (AlipayConfig)
+ password_config (PasswordComplexityConfig)
+ github_config (GithubConfig) - github侧oauth配置

## CustomField (object)
+ uuid (string)
+ name (string)
+ subject (string)
+ schema (object)
+ is_visible (boolean)

## NativeField (object)
+ uuid (string)
+ name (string)
+ subject (string)
+ schema (object)
+ key (string)
+ is_visible (boolean)
+ is_visible_editable (boolean)

## StorageConfig (object)
+ method (string)
+ minio_config (object)
    + end_point (string)
    + access_key (string)
    + secret_key (string)
    + secure (boolean)
    + location (string)
    + bucket (string)

## CompanyMetaInfo (CompanyConfig)
+ display_name (string)

## DingMetaInfo (object)
+ app_key (string)
+ corp_id (string)
+ qr_app_id (string)

## AlipayMetaInfo (object)
+ app_id (string)

## WorkWechatMetaInfo (object)
+ corp_id (string)

## AccountMetaInfo (object)
+ support_email (boolean) - 是否支持邮箱登录、找回密码、激活
+ support_mobile (boolean) - 是否支持手机登录、找回密码、激活
+ support_email_register (boolean) - 是否支持邮箱注册
+ support_mobile_register (boolean) - 是否支持手机注册
+ support_ding_qr (boolean) - 是否支持钉钉扫码登录
+ support_work_wechat_qr (boolean) - 是否支持企业微信扫码登录

## MetaInfo (object)
+ company_config (CompanyMetaInfo)
+ ding_config (DingMetaInfo)
+ account_config (AccountMetaInfo)
+ alipay_config (AlipayMetaInfo)
+ work_wechat_config (WorkWechatMetaInfo)

## MetaNodeInfo (object)
+ name (string)
+ slug (string)
+ node_uid (string) - 要新建分类时，需置于该节点下
+ nodes (array)
    + node (object)
        + name (string)
        + `node_uid` (string) - 比如 `g_role`
        + `node_subject` (string) - 比如 `role`

## LiteLog (object)
+ uuid (string)
+ user (object)
    + name (string)
    + username (string)
+ subject (string) - 事件类型
+ subject_verbose (string) - 事件类型-用于展示
+ summary (string) - 事件信息
+ created (string) - 发生时间

## Log (LiteLog)
+ detail (string) - 详细信息

## CrontabPlugin (object)
+ uuid
+ name
+ detail
+ import_path
+ is_active (boolean)
+ schedule

## MiddlewarePlugin (object)
+ uuid
+ name
+ detail
+ import_path
+ is_active (boolean)
+ order_no (number)

## I18NMobileConfig (object)
+ uuid (string) - 唯一标识
+ state (string) - 所属地区
+ state_code (string) - 区号
+ number_length (number) - 固定号码长度
+ start_digit (array[number]) - 首位数字限制集
+ is_active (boolean) - 是否启用

# Group Infrastructure
基础设施

## 图片验证码 [/service/captcha/]
### 获取验证码图片 [GET]
+ Response 200 (application/json)
    + Attributes
        + captcha_key (string)
        + captcha_url (string) - 完整url
### 校验验证码 [POST]
+ Request JSON Message
    + Attributes
        + captcha_key (string) -来自上文
        + captcha (string) - 用户输入
+ Response 200 (application/json)
成功
+ Response 400 (application/json)
失败


## 短信验证码-注册 [/service/sms/register/{?mobile,code}]

### 发送短信验证码 [POST]
+ Request JSON Message
    + Attributes
        + mobile (string, required)
        + captcha_key (string)
        + captcha (string)
+ Response 201 (application/json)

### 验证短信验证码 [GET]
+ Parameters
    + mobile (string) - 支持国际手机号，形如 `+86 18812341234`，作为URL QueryParams 时注意需要编码 -> `%2B86%2018813105748`
    + code (string)

+ Response 200 (application/json)
    + Attributes
        + sms_token (string)
        + expired (string)

+ Response 400 (application/json)
失败

## 短信验证码-登录 [/service/sms/login/{?mobile,code}]

### 发送短信验证码 [POST]
+ Request JSON Message
    + Attributes
        + mobile (string, required)
        + captcha_key (string)
        + captcha (string)
+ Response 201 (application/json)

### 验证短信验证码 [GET]
+ Parameters
    + mobile (string)
    + code (string)

+ Response 200 (application/json)
    + Attributes
        + sms_token (string)
        + expired (string)

+ Response 400 (application/json)
失败

## 短信验证码-重置密码 [/service/sms/reset_password/{?mobile,code}]

### 发送短信验证码 [POST]
+ Request JSON Message
    + Attributes
        + mobile (string, required)
        + username (string, required)
        + captcha_key (string)
        + captcha (string)
+ Response 201 (application/json)

### 验证短信验证码 [GET]
+ Parameters
    + mobile (string)
    + code (string)
+ Response 200 (application/json)
    + Attributes
        + sms_token (string)
        + expired (string)

+ Response 400 (application/json)
失败

## 短信验证码-激活账号 [/service/sms/activate_user/{?mobile,code}]
### 发送短信验证码 [POST]
+ Request JSON Message
    + Attributes
        + key (string, required) - 邀请码
+ Response 201 (application/json)

### 验证短信验证码 [GET]
+ Parameters
    + mobile (string)
    + code (string)

+ Response 200 (application/json)
    + Attributes
        + sms_token (string)
        + expired (string)

## 短信验证码-重置手机 [/service/sms/update_mobile/{?mobile,code}]

### 发送短信验证码 [POST]
+ Request JSON Message
    + Attributes
        + mobile (string, required) - 重置后的手机号
        + password (string)

### 验证短信验证码 [GET]
+ Parameters
    + mobile (string) - 支持国际手机号，形如 `+86 18812341234`
    + code (string)

+ Response 200 (application/json)
    + Attributes
        + sms_token (string)
        + expired (string)


## 短信验证码-通用 [/service/sms/]
### 发送短信验证码 [POST]
+ Request JSON Message
    + Attributes
        + mobile (string, required)
        + captcha_key (string)
        + captcha (string)
+ Response 201 (application/json)

### 验证短信验证码 [GET]
+ Parameters
    + mobile (string) - 支持国际手机号，形如 `+86 18812341234`，作为URL QueryParams 时注意需要编码 -> `%2B86%2018813105748`
    + code (string)

+ Response 200 (application/json)
    + Attributes
        + sms_token (string)
        + expired (string)

+ Response 400 (application/json)
失败

## 验证邮件-注册 [/service/email/register/{?email_token}]

### 发送验证邮件 [POST]
+ Request JSON Message
    + Attributes
        + email (string, required)
+ Response 201 (application/json)
### 校验邮件验证码 [GET]
+ Parameters
    + email_token (string)

+ Response 200 (application/json)
    + Attributes
        + email (string)

## 验证邮件-重置密码 [/service/email/reset_password/{?email_token}]

### 发送验证邮件 [POST]
+ Request JSON Message
    + Attributes
        + email (string, required)
        + username (string, required)
+ Response 201 (application/json)
### 校验邮件验证码 [GET]
+ Parameters
    + email_token (string)

+ Response 200 (application/json)
    + Attributes
        + email (string)
        + username (string)
        + name (string)

## 验证邮件-激活账号 [/service/email/activate_user/{?email_token}]

### 发送验证邮件 [POST]
+ Request JSON Message
    + Attributes
        + key (string, required) - 邀请码
+ Response 201 (application/json)

### 校验邮件验证码 [GET]
+ Parameters
    + email_token (string)

+ Response 200 (application/json)
    + Attributes
        + email (string)
        + username (string)
        + name (string)
        + key (string)

## 验证邮件-重置邮箱 [/service/email/update_email/{?email_token}]

### 发送验证邮件 [POST]
+ Request JSON Message
    + Attributes
        + email (string, required) - 重置后的邮箱
        + password (string, required)
+ Response 201 (application/json)

### 校验邮件验证码 [GET]
+ Parameters
    + email_token (string)

+ Response 200 (application/json)
    + Attributes
        + email (string)
        + username (string)
        + name (string)

# Group Statistics
统计数据
## 用户统计数据 [/statistics/user_statistic]
### 获取用户统计数据 [GET]
+ Response 200 (application/json)
    + Attributes
        + total_count (number)
        + active_count (number)

# Group User Center
该部分为用户向接口，本文档其余部分皆只对管理员开放

## 用户注册 [/ucenter/register/]

### 注册 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string)

        + sms_token (string)
        + email_token (string)
+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

## 用户登录 [/ucenter/login/]
无需登录。除特声明无需登录外，其余接口均需token
### 登录 [POST]
+ Request JSON Message
    + Attributes
        + username (string, optional)
        + private_email (string, optional)
        + mobile (string, optional)
        + password (string, optional)
        + sms_token (string, optional)
+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

## 钉钉登录 [/ucenter/ding/login/]
无需登录。除特声明无需登录外，其余接口均需token
https://open-doc.dingtalk.com/microapp/dev/about
https://open-doc.dingtalk.com/microapp/serverapi2/clotub

### 登录 [POST]
+ Request JSON Message
    + Attributes
        + code (string) - 钉钉登录码
+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

## 用户权限 [/ucenter/perm/]
需登录。只返回用户拥有的权限
只读

### 查询权限 [GET]
+ Response 200 (application/json)
    + Attributes
        + count
        + next
        + previous
        + results (array[UserPerm])


## 用户密码 [/ucenter/password/]

### 重置密码 [PUT]
无需登录
用于忘记密码时的重置密码、登录后的重置密码。

+ Request JSON Message
    + Attributes
        + username - 通过旧密码修改
        + old_password - 通过旧密码修改

        + mobile - 通过短信修改
        + sms_token - 通过短信修改

        + email - 通过邮箱修改
        + email_token - 通过邮箱修改

        + new_password (required)

+ Response 200 (application/json)

## 用户信息 [/ucenter/profile/]

需登录

### 获取自身信息 [GET]

+ Response 200 (application/json)
    + Attributes (UserProfile)

### 修改自身信息 [PATCH]

+ Request JSON Message (UserProfile)

+ Response 200 (application/json)
    + Attributes (UserProfile)


## 用户手机 [/ucenter/mobile/]
deprecated
### 修改手机 [PATCH]
+ Request JSON Message
    + Attributes
        + old_mobile_sms_token (string)
        + new_mobile_sms_token (string)
+ Response 200 (application/json)
    + Attributes
        + new_mobile (string)

## 用户联系方式 [/ucenter/contact/]

### 用户修改联系方式 [PATCH]
+ Request JSON Message
    + Attributes
        + email_token (string, optional)
        + sms_token (string, optional)
+ Response 200 (application/json)
    + Attributes
        + private_email
        + mobile

## 被邀请用户身份信息 [/ucenter/profile/invited/]

### 获取身份信息 [GET]
+ Response 200 (application/json)
    + Attributes(UserWithPerm)

### 配置信息 [PATCH]
+ Request JSON Message
    + Attributes
        + password (string, required)
        + username (string)
        + sms_token (string)
        + email_token (string)

+ Response 200 (application/json)
    + Attributes(UserWithPerm)

## 权限 [/auth/token/]

### 校验权限 [GET]
+ Request JSON Message
    + Attributes
        + perm_uid (string, optional)
        + app_uid (string, optional) - 限定返回的权限。此时返回的 perm_uid 不带前缀，形如 `manage`
        + oauth_client_id (string, optional) - 作用同 app_uid

+ Response 200 (application/json)  
    拥有该权限
    + Attributes (UserWithPerm)

+ Response 403 (application/json)
    Permission denied

## 第三方账号 [/ucenter/sub_account/{?domain}]
### 获取第三方账号 [GET]
+ Parameters
    + domain (string) - 登录页域名

+ Response 200 (application/json)
    + Attributes (object)
        + previous (string)
        + next (string)
        + count (number)
        + results (array[SubAccount]))

# Group Auth
以下部分均只对管理员开放
TODO: 校对

## 认证 [/auth/]

### 认证 [POST]
+ Request JSON Message
    + Attributes
        + username (string, required)
        + password (string, optional) - 若提供密码则对密码进行检查。
        + group (string, optional) - 用户处于子组中，也认为有权限
        + dept (string, optional) - 用户处于子部门中，也认为有权限
        + perm (string, optional) - 检查用户是否有特定权限

+ Response 200 (application/json)
    + Attributes
        + result (boolean) - 认证结果 (password) and (group or dept or perm)

## 登出 [/revoke/token/]

### 登出 [POST]
+ Request JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes

## 邀请码登录 [/auth/invitation_key/]

### 认证 [POST]
+ Request JSON Message
    + Attributes
        + mobile (string)
        + key (string)
+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

# Group User
用户管理

## 所有用户 [/user/{?keyword,wechat_unionid,name,name__icontains,username,username__icontains,email,email__icontains,private_email,private_email__icontains,mobile,mobile__icontains,gender,remark,remark__icontains,created__lte,created__gte,last_active_time__lte,last_active_time__gte,unbound_wechat,unbound_ding,unbound_qq,unbound_alipay,user_ids,usernames,group_uids,%2Dgroup_uids,perm_uids,%2Dperm_uids,sort,%2A__custom,%2A__lt__custom,%2A__lte__custom,%2A__gt__custom,%2A__gte__custom,page,page_size}]

### 创建用户 [POST]
+ Request JSON Message
    + Attributes
        + group_uids (array[string], optional)
        + dept_uids (array[string], optional)
        + node_uids (array[string], optional) - 此字段提供时会忽略`group_uids`,`dept_uids`
        + user (CreateUser)
+ Response 201 (application/json)
    + Attributes (Employee)

### 获取用户列表 [GET]

+ Parameters
    + keyword (string, optional) - 查询关键字，进行用户名、姓名、邮箱、手机号模糊搜索
    + wechat_unionid (string, optional)
    + name (string, optional) - 姓名精准搜索
    + name__icontains (string, optional) - 姓名模糊搜索
    + username (string, optional) - 用户名精准搜索
    + username__icontains (string, optional) - 用户名模糊搜索
    + email (string, optional)
    + email__icontains (string, optional)
    + private_email (string, optional)
    + private_email__icontains (string, optional)
    + mobile (string, optional)
    + mobile__icontains (string, optional)
    + gender (number, optional)
    + remark (string, optional)
    + remark__icontains (string, optional)
    + created__lte (string, optional)
    + created__gte (string, optional)
    + last_active_time__lte (string, optional)
    + last_active_time__gte (string, optional)
    + unbound_wechat (boolean, optional) - 未关联微信搜索;'true'表示搜索未关联微信的用户,'false'表示搜索关联微信的用户
    + unbound_ding (boolean, optional) - 未关联钉钉搜索;'true'表示搜索未关联钉钉的用户,'false'表示搜索关联钉钉的用户
    + unbound_qq (boolean, optional) - 未关联QQ搜索;'true'表示搜索未关联QQ的用户,'false'表示搜索关联QQ的用户
    + unbound_alipay (boolean, optional) - 未关联支付宝搜索;'true'表示搜索未关联支付宝的用户,'false'表示搜索关联支付宝的用户
    + user_ids (string, optional) - 指定用户id的搜索;形如'&=id1 id2 ... id3',参数间用空格分隔
    + usernames (string, optional) - 指定用户名的搜索;形如'&=username1 username2 ... username3',参数间用空格分隔
    + group_uids (string, optional) - 指定属于一些组的搜索;形如'&=group1 group2 ... group3',参数间用空格分隔
    + %2Dgroup_uids (string, optional) - 指定不属于一些组的搜索;形如'&=group1 group2 ... group3',参数间用空格分隔
    + perm_uids (string, optional) - 指定拥有一些权限的搜索;形如'&=perm1 perm2 ... perm3',参数间用空格分隔
    + %2Dperm_uids (string, optional) - 指定未拥有一些权限的搜索;形如'&=perm1 perm2 ... perm3',参数间用空格分隔
    + sort (string, optional) - 指定搜索结果按某字段顺序(逆序)输出;形如'&=condition1 -condition2 ... condition3',参数间用空格分隔,其中'-condition2'表示按照'condition2'字段逆序排序
    + %2A__custom (string, optional) - 自定义字段搜索,(`*`为自定义字段)
    + %2A__lt__custom (string, optional) - 自定义字段范围搜索,(`*`为自定义字段);注意:目标字段在初始化时,字段值需为string类型,否则将导致搜索失败
    + %2A__gt__custom (string, optional) - 自定义字段范围搜索,(`*`为自定义字段);注意:目标字段在初始化时,字段值需为string类型,否则将导致搜索失败
    + %2A__lte__custom (string, optional) - 自定义字段范围搜索,(`*`为自定义字段);注意:目标字段在初始化时,字段值需为string类型,否则将导致搜索失败
    + %2A__gte__custom (string, optional) - 自定义字段范围搜索,(`*`为自定义字段);注意:目标字段在初始化时,字段值需为string类型,否则将导致搜索失败
    + page (number, optional)
        + default: 1
    + page_size (number, optional)
        + default: 30

不考虑层级，单纯返回所有用户

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + previous (string)
        + next (string)
        + results (array[Employee])


## 所有独立用户 [/user/isolated/]

### 获取所有独立用户 [GET]
+ request JSON Message
    + Attributes
        + page_size (number)
            - default: 30
        + page (number)
            - default: 1
+ Response 200 (application/json)
    + Attributes
        + count (number)
        + previous (string)
        + next (string)
        + results (array[User])

## 特定用户 [/user/{username}/]

+ Parameters
    + username (string) - 用户唯一标识

### 获取用户信息 [GET]
+ Request JSON Message
+ Response 200 (application/json)
    + Attributes (Employee)

### 修改用户信息 [PATCH]

+ Request JSON Message
    + Attributes (User)

+ Response 204 (application/json)
    + Attributes (Employee)

### 删除用户 [DELETE]

+ Response 204 

## 普通用户查看他人信息 [/ucenter/user/{username}/]
+ Parameters
    + username (string) - 用户唯一标识

### 普通用户获取他人信息 [GET]

+ Response 200 (application/json)
    + Attributes (User)

## 用户所属组 [/user/{username}/group/]
数据仅包括用户直接所属的组
+ Parameters
    + username (string) - 用户唯一标识

### 获取用户所属组 [GET]

+ Response JSON Message
+ Request 200 (application/json)
    + Attributes
        + groups (array[Group])

### 修改所属组 [PATCH]

+ Request JSON Message
    + Attributes
        + group_uids (array[string])
        + subject (enum[string])
            + add - 添加此人至这些组
            + delete - 将此人从这些组移除
            + override - 重置组，慎用
+ Request 204 (application/json)
    + Attributes
        + groups (array[Group]) - 操作后所属组


## 用户所属部门 [/user/{username}/dept/]
数据仅包括用户直接所属的部门
+ Parameters
    + username (string) - 用户唯一标识

### 获取用户所属部门 [GET]

+ Response JSON Message
+ Request 200 (application/json)
    + Attributes
        + depts (array[Dept])

### 修改所属部门 [PATCH]

+ Request JSON Message
    + Attributes
        + dept_uids (array[string])
        + subject (enum[string])
            + add - 添加此人至这些部门
            + delete - 将此人从这些部门移除
            + override - 重置部门，慎用
+ Request 204 (application/json)
    + Attributes
        + depts (array[Dept]) - 操作后所属部门

## 用户所属节点 [/user/{username}/node/]
数据仅包括用户直接所属的节点
+ Parameters
    + username (string) - 用户唯一标识

### 获取用户所属节点 [GET]

+ Response JSON Message
+ Request 200 (application/json)
    + Attributes
        + nodes (array[Node])

### 修改所属节点 [PATCH]

+ Request JSON Message
    + Attributes
        + node_uids (array[string])
        + subject (enum[string])
            + add - 添加此人至这些节点
            + delete - 将此人从这些节点移除
            + override - 重置节点，慎用
+ Request 204 (application/json)
    + Attributes
        + nodes (array[Node]) - 操作后所属节点

## 外部用户准换为内部用户 [/user/{username}/convert/intra/]
+ Parameters
    + username (string) - 用户唯一标识

### 外部用户准换为内部用户 [PATCH]
+ Request JSON Message
    + Attributes (User)
+ Request 200 (application/json)
    + Attributes
        + nodes (Employee)

## 用户密码 [/user/{username}/password/]
仅对主管理员开放
+ Parameters
    + username (string) - 用户唯一标识
### 修改用户密码 [PATCH]
+ Request JSON Message
    + Attributes
        + password (string) - 新密码
        + require_reset_password (boolean) - 登录后是否需要修改密码

### 内部用户转换为外部用户 [/user/{username}/convert/extern/]
+ Parameters
    + username (string) - 用户唯一标识

### 内部用户转换为外部用户 [PATCH]
+ Request JSON Message
    + Attributes (User)
+ Request 200 (application/json)
    + Attributes
        + nodes (Employee)

# Group Dept
部门管理

## 部门列表 [/dept/]

### 获取部门列表 [GET]

+ Request JSON Message
    + Attributes
        + name (boolean) - 部门名称，模糊搜索
+ + Response 200 (application/json)
    + Attributes (object)
        + count (number)
        + next (string)
        + previous (string)
        + results (array[Dept])

## 部门信息 [/dept/{uid}/]

+ Parameters
    + uid (string) - 部门唯一标识。root特指全公司。

### 获取部门信息 [GET]

+ Response 200 (application/json)
    + Attributes (DeptDetail)


### 修改部门信息 [PATCH]
+ Request JSON Message
    + Attributes (DeptDetail)

+ Response 200 (application/json)
    + Attributes (DeptDetail)


### 删除部门 [DELETE]
需先清空子节点
+ Response 204 

## 部门及其子孙部门列表 [/dept/{uid}/list/]

将某部门下的子树以列表形式返回，包括该部门自身，前序遍历。

+ Parameters
    + uid (string) - 部门唯一标识。root特指全公司。

### 获取部门及其子孙部门列表 [GET]

+ Response 200 (application/json)
    + Attributes (array[DeptDetail])

## 部门结构树 [/dept/{uid}/tree/]
数据包括从该节点起始的完整树
+ Parameters
    + uid (string) - 部门唯一标识。root特指全公司。

### 获取完整部门结构树 [GET]

+ Request JSON Message
    + Attributes
        + user_required (boolean) - 是否需要成员信息
            - default: false
+ Response 200 (application/json)
    + Attributes (DeptTree)  - DeptOnlyTree if not user_required



## 部门子部门 [/dept/{uid}/dept/]

+ Parameters
    + uid (string) - 部门唯一标识。root特指全公司。

### 获取子部门 [GET]
+ Response (application/json)
    + Attributes
        + depts (array[Dept])


### 创建子部门 [POST]
+ Request JSON Message
    + Attributes (Dept)
+ Response 201 (application/json)
    + Attributes (Dept)

### 调整子部门 [PATCH]
+ Request JSON Message
    + Attributes
        + dept_uids (array[string])
        + subject (enum[string]) - 操作类型
            + sort - 对指定人按指定位置进行排序
            + add - 将某部门添加至该部门

+ Response 204 (application/json)
    + Attributes
        + depts (array[Dept]) - 操作后有哪些子部门



## 部门人员 [/dept/{uid}/user/]

数据仅限于子一级

+ Parameters
    + uid (string) - 部门唯一标识。root特指全公司。

### 获取部门人员 [GET]

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + previous
        + next
        + results (array[User])

### 调整成员用户 [PATCH]
+ Request JSON Message
    + Attributes
        + `user_uids` (array[string]) - array of user.username
        + `dept_uids` (array[string]) - array of dept.uid，仅当`move_out`时用到
        + subject (enum[string]) - 操作类型
            + add - 添加这些人至该部门
            + delete - 将这些人从该部门移除
            + override - 重置部门成员，慎用
            + sort - 对指定人按指定位置进行排序
            + move_out - 将这些人从该部门移除，并加到指定部门
+ Response 204 (application/json)
    + Attributes
        + users (array[User]) - 操作后部门中有哪些人


# Group Group

## 组列表 [/group/]

### 获取组列表 [GET]

+ Request JSON Message
    + Attributes
        + name (boolean) - 组名称，模糊搜索
+ + Response 200 (application/json)
    + Attributes (object)
        + count (number)
        + next (string)
        + previous (string)
        + results (array[Group])

## 组信息 [/group/{uid}/]

+ Parameters
    + uid (string) - 组唯一标识。root特指最顶级组。

### 获取组信息 [GET]
+ Response 200 (application/json)
    + Attributes (GroupDetail)

### 修改组信息 [PATCH]
+ Request JSON Message
    + Attributes (GroupDetail)
+ Response 200 (application/json)
    + Attributes (GroupDetail)

### 删除组 [DELETE]
需先清空子节点
+ Response 204 

## 组及其子孙组列表 [/group/{uid}/list/]
将某组下的子树以列表形式返回，包括该组自身，前序遍历。

+ Parameters
    + uid (string) - 组唯一标识。


### 获取组及其子孙组列表 [GET]

+ Response 200 (application/json)
    + Attributes (array[GroupDetail])

## 组结构 [/group/{uid}/tree/]

数据包括从该节点起始的完整树
+ Parameters
    + uid (string) - 组唯一标识。root特指最顶级组。

### 获取完整组结构 [GET]

+ Request JSON Message
    + Attributes
        + `user_required` (boolean) - 是否需要成员信息
            - default: false

+ Response 200 (application/json)
    + Attributes (GroupTree) - GroupOnlyTree if not user_required


## 组子组 [/group/{uid}/group/]
数据仅限于子一级
+ Parameters
    + uid (string) - 组唯一标识。root特指最顶级组，其子节点即为角色组。

### 获取子组 [GET]

+ Response 200 (application/json)
    + Attributes
        + groups (array[Group])

### 创建子组 [POST]
+ Request JSON Message
    + Attributes (Group)
+ Response 201 (application/json)
    + Attributes (Group)

### 调整子组 [PATCH]
+ Request (application/json)
    + Attributes
        + `group_uids` (array[string]) - array of uid
        + subject (enum[string]) - 操作类型
            + add - 添加这些组至该组
            + sort - 对指定子组按指定位置进行排序

+ Response 204
    + Attributes
        + groups (array[Group]) - 操作后该组中有哪些子组


## 组人员 [/group/{uid}/user/]
数据仅限于子一级
+ Parameters
    + uid (string) - 组唯一标识。root特指最顶级组。

### 获取组员 [GET]
+ Request
    + Attributes
        + uids (string) - 附加查询组，取结果交集。格式上以|分隔，形如 group_1|group_2

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + previous
        + next
        + results (array[User])

### 调整成员用户 [PATCH]
+ Request (application/json)
    + Attributes
        + `user_uids` (array[string]) - array of username
        + `group_uids` (array[string]) - array of group.uid，仅当`move_out`时用到
        + subject (enum[string]) - 操作类型
            + add - 添加这些人至该组
            + delete - 将这些人从该组移除
            + override - 重置组用户，慎用
            + sort - 对指定人按指定位置进行排序
            + move_out - 将这些人从该部门移除，并加到指定部门

+ Response 204 (application/json)
    + Attributes
        + users (array[User]) - 操作后该组中有哪些人


# Group Node

Node 为 Dept 和 Group 的抽象

## 节点信息 [/node/{node_uid}/{?ignore_user}]

+ Parameters
    + `node_uid` (string) - 节点唯一标识。
    + `ignore_user` (boolean) - 用于删除节点。当true时，若节点下有人员存在时，会先将人员从节点内删除，再删除此节点

### 获取节点信息 [GET]
+ Response 200 (application/json)
    + Attributes (NodeWithParent)

### 修改节点信息 [PATCH]
+ Request JSON Message
    + Attributes (Node)

+ Response 200 (application/json)
    + Attributes (NodeWithParent)

### 删除节点 [DELETE]
需先清空子节点
+ Response 204 

+ Response 400 (application/json)
{
    "node": [
        "protected_by_child_node",
        "protected_by_child_user",
    ]
}

## 用户查看节点信息 [/ucenter/node/{node_uid}/]

+ Parameters
    + `node_uid` (string) - 节点唯一标识。

### 获取节点信息 [GET]
+ Response 200 (application/json)
    + Attributes (NodeWithParent)


## 节点及其子孙节点列表 [/node/{node_uid}/list/]
将某节点下的子树以列表形式返回，包括该节点自身，前序遍历。
+ Parameters
    + `node_uid` (string) - 节点唯一标识。

### 获取节点及其子孙节点列表 [GET]

+ Response 200 (application/json)
    + Attributes (array[NodeWithParent])


## 管理员访问节点下结构 [/node/{node_uid}/tree/]
管理员访问到的数据将由管理范围决定

数据包括从该节点起始的完整树
+ Parameters
    + node_uid (string) - 节点唯一标识。

### 获取完整树结构 [GET]

+ Request JSON Message
    + Attributes
        + user_required (boolean) - 是否需要成员信息
            - default: false

+ Response 200 (application/json)
    + Attributes (NodeTree) - NodeOnlyTree if not user_required

## 员工访问节点下结构 [/ucenter/node/{node_uid}/tree/]
普通用户访问到的数据将由节点可见范围决定

数据包括从该节点起始的完整树
+ Parameters
    + node_uid (string) - 节点唯一标识。

### 获取完整树结构 [GET]

+ Request JSON Message
    + Attributes
        + user_required (boolean) - 是否需要成员信息
            - default: false

+ Response 200 (application/json)
    + Attributes (NodeTree) - NodeOnlyTree if not user_required


## 子管理员组列表 [/node/manager/node/]
除查询外的其他操作，请使用节点通用接口
### 获取子管理员列表 [GET]
+ Response 200 (application/json)
    + Attributes
        + nodes (array)
            + node (Node)
                + manager_group (VerboseManagerGroup)
                + users (array)
                    + user
                        + username
                        + name

## 节点下直属子节点 [/node/{node_uid}/node/]
TODO: 可见权限的处理

+ Parameters
    + `node_uid` (string) - 节点唯一标识。

### 获取子节点 [GET]

+ Response 200 (application/json)
    + Attributes
        + nodes (array[Node])

### 创建子节点 [POST]
+ Request JSON Message
    + Attributes (Node)
+ Response 201 (application/json)
    + Attributes (Node)

### 调整子节点 [PATCH]
+ Request (application/json)
    + Attributes
        + `node_uids` (array[string]) - array of uid
        + subject (enum[string]) - 操作类型
            + add - 添加这些节点至该节点
            + sort - 对指定子节点按指定位置进行排序

+ Response 204
    + Attributes
        + groups (array[Node]) - 操作后该节点中有哪些子节点

+ Response 400 (application/json)
{
    "node": [
        "deadlock",
        "unrelated",
        "across_scope",
    ]
}


## 节点下直属人员 [/node/{node_uid}/user/{?name,username,mobile,email,before_created,after_created,before_last_active_time,after_last_active_time}]


数据仅限于子一级，参数限于{node_uid}为‘g_'开头的请求有效
+ Parameters
    + `node_uid` (string) - 节点唯一标识。
    + `name` (string) - 姓名。
    + `username` (string) - 用户名
    + `mobile` (string) - 手机号
    + `email` (string) - 邮箱
    + `before_created` (string) - 在这个时间之前创建的用户
    + `after_created` (string) - 在这个时间之后创建的用户
    + `before_last_active_time` (string) - 在这之前活跃的用户
    + `after_last_active_time` (string) - 在这之后活跃的用户

### 获取直属人员 [GET]
+ Request
    + Attributes
        + node_uids (string) - 附加查询组，取结果交集。格式上以|分隔，形如 group_1|group_2 TODO：未兼容

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + previous
        + next
        + results (array[User])

### 调整成员用户 [PATCH]
+ Request (application/json)
    + Attributes
        + `user_uids` (array[string]) - array of username
        + `node_uids` (array[string]) - array of node.node_uid，仅当`move_out`时用到。TODO： 目前还不支持跨dept、group使用
        + subject (enum[string]) - 操作类型
            + add - 添加这些人至该节点
            + delete - 将这些人从该节点移除
            + override - 重置节点用户，慎用
            + sort - 对指定人按指定位置进行排序
            + move_out - 将这些人从该节点移除，并加到指定节点

+ Response 204 (application/json)
    + Attributes
        + users (array[User]) - 操作后该节点中有哪些人
+ Response 400 (application/json)
{
    "user": "unrelated"
}

# Group Perm

## 所有权限 [/perm/{?action,action_except,scope,owner_subject,name}]

### 获取所有权限 [GET]
+ Parameters
    + action (string) - 特定操作
    + `action_except` (string) - 排除某操作，惯用`action_except=access`获取应用内权限
    + scope (string) - 与应用uid对应，惯用该字段获取某应用下权限
    + name (string) - 权限名称
    + `owner_subject` (enum[string]) - 需要提供权限所有者列表，并指明需要的类型
        + all
        + user
        + dept
        + role
        + label
        + ...
+ Response 200 (application/json)
    + Attributes
        + count
        + next
        + previous
        + results (array[PermWithOwner])

### 创建权限 [POST]
+ request JSON Message
    + Attributes (object)
        + scope (string) - 应用uid
        + name (string)
+ Response 200 (application/json)
    + Attributes(Perm)


## 特定权限 [/perm/{uid}/]

+ Parameters
    + uid (string) - 权限唯一标识

### 查询权限信息 [GET]
+ Response 200 (application/json)
    + Attributes (Perm)

### 更新权限信息 [PATCH]
+ Request (application/json)
    + Attributes (Perm)

+ Response 200 (application/json)
    + Attributes (Perm)

## 权限所有者 [/perm/{uid}/owner/{?owner_subject,value,status}]

该接口内的uid，对于user为username，对于node为node_uid

+ Parameters
    + uid (string) - 权限唯一标识
    + owner_subject (enum[string], required) - 权限所有者类型
        + all
        + user
        + dept
        + role
        + label
        + ...
    + value (boolean, optional) - 最终判定结果
    + status (enum[number], optional) - 授权状态
        + -1 - 显式拒绝，即黑名单
        + 0 - 随上级决定
        + 1 - 显式授权，即白名单

### 获取某权限指定类型的所有者 [GET]

+ Response 200 (application/json)
    + Attributes (object)
        + count (number)
        + next (string)
        + previous (string)
        + results (array)
            + owner (object)
                + uid (string)
                + name (string)
                + owner (string)

### 批量显式授权、拒绝或置为默认 [PATCH]

仅按提供的数据做局部修改

+ Response 200 (application/json)
    + Attributes (object)
        + clean (boolean, optional) - 是否重置所有owner的status为0
        + user_perm_status (array, optional)
            + owner_perm (object)
                + uid (string) - username
                + status (number) - -1,0,1
        + node_perm_status (array, optional)
            + owner_perm (object)
                + uid (string) - node_uid
                + status (number) - -1,0,1

## 用户权限 [/perm/user/{username}/{?action,action_except,scope}]
+ Parameters
    + username (string) - 用户唯一标识
    + action (string) - 特定操作
    + `action_except` (string) - 排除某操作，惯用`action_except=access`获取应用内权限
    + scope (string) - 与应用uid对应，惯用该字段获取某应用下权限

### 获取用户所有权限 [GET]
包括所有授权、未授权的权限

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + next (string)
        + previous (string)
        + results (array[UserPerm])

### 更新用户权限 [PATCH]

+ request JSON Message
    + Attributes
        + perm_statuses (array)
            + perm_status (object)
                + uid (string) - perm_uid
                + status (number)

+ Response 200 (application/json)
    + Attributes (array[UserPerm]) - 修改的用户权限


## 用户权限列表 [/user/{username}/perm/]

### 刷新用户权限 [PUT]
用于获取实时权限判定结果

+ Response 200 (application/json)
    + Attributes
        + task_id
        + task_msg

## 用户权限详情 [/user/{username}/perm/{uid}/]
+ Parameters
    + username (string) - 用户名
    + uid (string) - 权限唯一标识

### 获取用户权限详情 [GET]
包括权限来源

+ Response 200 (application/json)
    + Attributes (UserPermDetail)

### 刷新用户权限详情 [PUT]

用于获取实时权限判定结果

+ Response 200 (application/json)
    + Attributes (UserPermDetail)

## 用户权限结果 [/user/{username}/perm/{uid}/result/]
+ Parameters
    + username (string) - 用户名
    + uid (string) - 权限唯一标识

### 获取用户权限结果 [GET]
+ Response 200 (application/json)
    + Attributes (UserPerm)


## 部门权限 [/perm/dept/{uid}/{?action,action_except,scope}]

+ Parameters
    + uis (string) - 部门唯一标识
    + action (string) - 特定操作
    + `action_except` (string) - 排除某操作，惯用`action_except=access`获取应用内权限
    + scope (string) - 与应用uid对应，惯用该字段获取某应用下权限

### 获取部门所有权限 [GET]
包括所有授权、未授权的权限

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + next (string)
        + previous (string)
        + results (array[PermResult]))

### 更新部门权限 [PATCH]

+ request JSON Message
    + Attributes
        + perm_statuses (array)
            + perm_status (object)
                + uid - perm_uid
                + status (enum[number])
                    - 1 - 显式拒绝
                    - 0 - 随上级决定
                    - 1 - 显式授

+ Response 200 (application/json)
    + Attributes (array[PermResult]) - 修改的部门权限

## 组权限 [/perm/group/{uid}/{?action,action_except,scope}]

+ Parameters
    + uis (string) - 组唯一标识
    + action (string) - 特定操作
    + `action_except` (string) - 排除某操作，惯用`action_except=access`获取应用内权限
    + scope (string) - 与应用uid对应，惯用该字段获取某应用下权限

### 获取组所有权限 [GET]
包括所有授权、未授权的权限

+ Response 200 (application/json)
    + Attributes
        + count (number)
        + next (string)
        + previous (string)
        + results (array[PermResult])

### 更新组权限 [PATCH]

+ request JSON Message
    + Attributes
        + perm_statuses (array)
            + perm_status (object)
                + uid - perm_uid
                + status (enum[number])
                    - 1 - 显式拒绝
                    - 0 - 随上级决定
                    - 1 - 显式授

+ Response 200 (application/json)
    + Attributes (array[PermResult]) - 修改的组权限

## 节点权限 [/perm/node/{node_uid}/{?action,action_except,scope}]

+ Parameters
    + node_uid (string) - 节点唯一标识
    + action (string) - 特定操作
    + `action_except` (string) - 排除某操作，惯用`action_except=access`获取应用内权限
    + scope (string) - 与应用uid对应，惯用该字段获取某应用下权限

### 获取节点所有权限 [GET]
包括所有授权、未授权的权限

+ Response 200 (application/json)
    + Attributes (object)
        + count (number)
        + next (string)
        + previous (string)
        + results (array[PermResult])

### 更新组权限 [PATCH]

+ request JSON Message
    + Attributes
        + perm_statuses (array)
            + perm_status (object)
                + uid (string) - perm_uid
                + status (enum[number])
                    - 1 - 显式拒绝
                    - 0 - 随上级决定
                    - 1 - 显式授权

+ Response 200 (application/json)
    + Attributes (array[PermResult]) - 修改的组权限


# Group APP

## 所有应用 [/app/{?name,node_uid,user_uid,owner_access}]
受管理员管理范围影响

+ Parameters
    + name (string, optional)
    + node_uid (string) - 查询该节点的权限
    + user_uid (string) - 查询该用户权限
    + owner_access (boolean) - 限定访问权限结果

### 获取所有应用 [GET]
+ Response 200 (application/json)
    + Attributes (object)
        + previous (string)
        + next (string)
        + count (number)
        + results (array[APPWithAccess])

### 创建应用 [POST]
+ request JSON Message
    + Attributes (APP)

+ Response 201 (application/json)
    + Attributes (APP)

## 普通用户可见应用 [/ucenter/apps/{?name}]
由有无可访问权限决定

+ Parameters
    + name (string, optional)

### 普通用户获取可见应用列表 [GET]
+ Response 200 (application/json)
    + Attributes (array[PublicAPP])


## 特定应用 [/app/{uid}/]

+ Parameters
    + uid (string) - 应用唯一标识。

### 获取特定应用 [GET]

+ Response 200 (application/json)
    + Attributes (APP)

### 修改应用 [PATCH]

+ Request JSON Message
    + Attributes (APP)

+ Response 204 (application/json)
    + Attributes (APP)

### 删除应用 [DELETE]

+ Response 204 (application/json)

## 应用 OAuth2.0 Client [/app/{uid}/oauth/]
+ Parameters
    + uid (string) - 应用唯一标识。

### 注册应用 [POST]
+ request JSON Message
    + Attributes
        + redirect_uris - callback url

+ Response 200 (application/json)
此应用存在，修改成功(启用OAuth并配置redirect_uris)
    + Attributes (OAuthAPP)

+ Response 201 (application/json)
此应用不存在，新建成功
    + Attributes (OAuthAPP)
    
## 应用 OpenID Connect Client [/app/{uid}/oauth/]
+ Parameters
    + uid (string) - 应用唯一标识。

### 注册应用 [POST]
+ request JSON Message
    + Attributes
        + redirect_uris - callback url
        + response_type
        + client_type
        
+ Response 200 (application/json)
此应用存在，修改成功(启用OAuth并配置redirect_uris)
    + Attributes (OAuthAPP)

+ Response 201 (application/json)
此应用不存在，新建成功
    + Attributes (OAuthAPP)

### 授权请求 [/app/oauth/authorize/{?client_id,scope,response_type, state, nonce, code_challenge, code_challenge_method, redirect_uri, oneid_token}]

+ Parameters
    + client_id (string) - OpenID Connect客户端标识符。
    + response_type (string) - 用于确定要使用的授权处理流程，包括从使用的端点返回的参数。
    + scope (string) - OpenID Connect请求必须包含openid范围值。如果不存在openid范围值，则行为完全不确定。可能存在其他范围值。实现所不能理解的作用域值应该被忽略。
    + state (string) - 不透明的值，用于维持请求和回调之间的状态。
    + nonce (string) - 字符串值，用于将客户端会话与ID令牌相关联，并减轻重放攻击。该值将未经修改地从身份验证请求传递到ID令牌。随机数值中必须存在足够的熵， 以防止攻击者猜测值。
    + code_challenge (string) - 用于通过本地客户端的 Proof Key for Code Exchange (PKCE) 保护授权代码授权。 如果包含 code_challenge_method，则需要。
    + code_challenge_method (string) - 用于为 code_challenge 参数编码 code_verifier 的方法。可选值为：plain、S256
    + redirect_uri (string) - 响应将发送到的重定向URI。
    + oneid_token (string) - ArkID用户的token字段值
    
#### [GET]

+ Response 302 ()
    + Redirect Uri
        + [<redirect_uri>/{?code, state}]
    + Parameters
        + code (string) - 应用程序请求的authorization_code。应用程序可以使用授权代码请求目标资源的访问令牌。Authorization_codes的生存期较短，通常在约10分钟后即过期。
        + state (string) - 来自上文。如果请求中包含状态参数，响应中就应该出现相同的值。应用程序应该验证请求和响应中的状态值是否完全相同。

### 令牌端点 [/app/oauth/token/]

#### [POST]

+ Request Form-Data Message
    + Attributes
        + code (string) - 应用程序请求的 authorization_code。
        + client_id (string) - OpenID Connect客户端标识符。
        + client_secret (string) - 在应用程序注册门户中为应用程序创建的应用程序机密。
        + redirect_uri (string) - 用于获取authorization_code的相同redirect_uri 值。
        + grant_type (string) - 必须是授权代码流的 authorization_code。
        + code_verifier (string) - 用于获取authorization_code的code_verifier。 如果在授权码授权请求中使用PKCE，则需要。
        
+ Response 200 (application/json)
    + Attributes (object)
        + access_token (string)
        + expires_in (string)
        + token_type (string)
        + scope (string)
        + refresh_token (string)
        + id_token (string)

### 用户端点 [/app/oauth/oidc/userinfo/]

#### [GET]

+ Request JSON Message
    + Headers Attributes
        + Authorization (string) - 形如 Bearer <access_token>，用于提供令牌给授权服务器验证。

+ Response 200 (application/json)
    + Attributes (object)
        + sub (string)
        + preferred_username (string)
        + email (string)

### 授权端点公钥信息 [/app/oauth/oidc/jwks/]

#### [GET]

+ Response 200 (application/json)
    + Attributes (object)
        + keys (array[KeyResult])

### 授权端点动态发现协议 [/app/oauth/.well-known/openid-configuration/]

#### [GET]

+ Response 200 (application/json)
    + Attributes (object)
        + issuer (string)
        + scopes_supported (array[ScopeResult])
        + authorization_endpoint (string)
        + token_endpoint (string)
        + userinfo_endpoint (string)
        + introspection_endpoint (string)
        + response_types_supported (array[ResponseTypeResult])
        + jwks_uri (string)
        + id_token_signing_alg_values_supported (array[SigningAlgResult])
        + subject_types_supported (array[KeyResult])
        + token_endpoint_auth_methods_supported (array[AuthMethodResult])

### 令牌内省 [/app/oauth/oidc/introspect/{?token}]

+ Parameters
    + token (string) - 访问令牌。
    
### [GET]

+ Response 200 (application/json)
    + Attributes (object)
        + active (boolean)
        + scope (string)
        + exp (timestamp)

# Group Shortcut

## 指定对象信息 [/slice/{?node_uids,user_uids,app_uids}]

+ Parameters
    + node_uids (array[string])
    + user_uids (array[string]) - username
    + app_uids (array[string])

### 根据uid获取指定对象信息-POST [POST]

+ Request JSON Message
    + Attributes
        + node_uids (array[string])
        + user_uids (array[string]) - username
        + app_uids (array[string])
+ Response 200 (application/json)
    + Attributes
        + apps (array[APP])
        + users (array[User])
        + nodes (array[NodeDetail])

### 根据uid获取指定对象信息-GET [GET]
+ Response 200 (application/json)
    + Attributes
        + apps (array[APP])
        + users (array[User])
        + nodes (array[NodeDetail])

## 删除指定对象 [/slice/delete/]
### 根据uid批量删除指定对象 [POST]
+ Request JSON Message
    + Attributes
        + user_uids (array[string]) - username
+ Response 200 (application/json)
    + Attributes
        + user_uids (array[string]) - username


# Group Config
全局配置

## 全局配置 [/config/]

仅管理员可见

### 获取当前配置 [GET]
+ Response 200 (application/json)
    + Attributes (Config)

### 修改当前配置 [PATCH]
+ request JSON Message
    + Attributes (Config)
+ Response 200 (application/json)
    + Attributes (Config)

## 主管理员 [/config/admin/]
仅主管理员可见

### 修改主管理员 [PATCH]
+ Request JSON Message
    + Attributes
        + old_admin_sms_token (string)
        + new_admin_sms_token (string)
+ Response 200 (application/json)
    + Attributes
        + new_admin_username (string)

### 获取主管理员详情 [GET]
+ Response 200 (application/json)
    + Attributes (User)

## 自定义字段 [/config/custom/field/{subject}/]

+ Parameters
    + subject (enum[string]) - 字段分类
        - user - 内部用户
        - extern_user - 外部用户

### 获取自定义字段列表 [GET]
+ Response 200 (application/json)
    + Attributes (array[CustomField])

### 添加自定义字段 [POST]
+ request JSON Message
    + Attributes (CustomField)
+ Response 200 (application/json)
    + Attributes (CustomField)

## 特定自定义字段 [/config/custom/field/{subject}/{uuid}/]

### 获取特定自定义字段 [GET]
+ Response 200 (application/json)
    + Attributes (CustomField)

### 修改特定自定义字段 [PATCH]
+ request JSON Message
    + Attributes (CustomField)
+ Response 200 (application/json)
    + Attributes (CustomField)

### 删除特定自定义字段 [DELETE]
+ Response 204

## 原生字段 [/config/native/field/{subject}/]

+ Parameters
    + subject (enum[string]) - 字段分类
        - user - 用户
        - extern_user - 外部用户

### 获取原生字段列表 [GET]
+ Response 200 (application/json)
    + Attributes (array[NativeField])

## 特定原生字段 [/config/native/field/{subject}/{uuid}/]

### 获取特定原生字段 [GET]
+ Response 200 (application/json)
    + Attributes (NativeField)

### 修改特定原生字段 [PATCH]
+ request JSON Message
    + Attributes (NativeField)
+ Response 200 (application/json)
    + Attributes (NativeField)

## 文件存储 [/config/storage/]

### 获取文件存储方式和minio配置信息 [GET]
+ Response 200 (application/json)
    + Attributes (StorageConfig)

### 修改文件存储方式和minio配置信息 [PATCH]
+ request JSON Message
    + Attributes (StorageConfig)
+ Response 200 (application/json)
    + Attributes (StorageConfig)

## 国际手机接入 [/config/i18n_mobile/]

### 添加接入配置 [POST]

+ request JSON Message
    + Attributes (I18NMobileConfig)

+ Response 200 (application/json)
    + Attributes (I18NMobileConfig)

### 获取接入配置 [GET]
+ Response 200 (application/json)
    + Attributes (array[I18NMobileConfig])

## 指定国际手机接入 [/config/i18n_mobile/{uuid}/]

+ Parameters
    + uuid (string) - 接入配置的唯一标识

### 修改接入配置 [PATCH]

+ request JSON Message
    + Attributes (I18NMobileConfig)

+ Response 200 (application/json)
    + Attributes (I18NMobileConfig)

### 删除接入配置 [DELETE]
+ Response 204

# Group Meta

## 基本信息 [/meta/]

匿名可见

### 获取当前基本信息 [GET]
+ Response 200 (application/json)
    + Attributes (MetaInfo)

## 组织架构基本信息 [/meta/node/]

登录可见

### 获取组织架构基本信息 [GET]
+ Response 200 (application/json)
    + Attributes (array[MetaNodeInfo])

## 日志基本信息 [/meta/log/]
管理员可见

### 获取日志基本信息 [GET]
+ Response 200 (application/json)
    + Attributes (array)
        + subject_item (object)
            + name (string)
            + subject (string)

## 内置权限基本信息 [/meta/perm/]
仅超级管理员可见

### 获取权限基本信息 [GET]
+ Response 200 (application/json)
    + Attributes (array)
        + subject_item (object)
            + name (string)
            + uid (string)

# Group Tasks
事件中心

## 导入钉钉数据 [/task/import/ding/]
### 触发导入 [GET]
+ Response 200 (application/json)
    + Attributes (object)
        + task_id (string)
        + task_msg (string)

## 任务结果 [/task/{task_id}/result/]

+ Parameters
    + task_id (string) - 任务事件唯一标识

### 查询任务结果 [GET]
+ Response 200 (application/json)
    + Attributes (object)
        + status (enum[number])
            + 1 - waiting
            + 2 - doing
            + 3 - failed
            + 4 - success
        + status_raw (string)
        + result (string)


# Group Events

## 邀请注册 [/invitation/user/{username}/]

+ Parameters
    + username (string) - 用户唯一标识(邀请的前提是先在后台事先添加该用户)

### 生成邀请码 [POST]

+ request JSON Message
    + Attributes
        + duration_minutes (number, optional) - 有效时长，单位分钟

+ Response 200 (application/json)
    + Attributes
        + uuid (string)
        + inviter (string)
        + invitee (string)
        + key (string) -被邀请用户持该key登录
        + expired_time (string)


# Group Migration

## 导出用户数据 [/migration/user/csv/export/]

### 导出用户数据 [POST]

+ request JSON Message
    + Attributes
        + user_uids (array[string]) - 用户名列表

+ Response 200 (text/csv)

## 导入用户数据 [/migration/user/csv/import/]

### 导入用户数据 [POST]

+ Request (multipart/form-data; boundary=---BOUNDARY)

-----BOUNDARY
Content-Disposition: form-data; name='users'
Content-Type: text/csv

username,name,email,private_email,mobile,gender,avatar,position,employee_number
admin,,,,a,0,,,
-----BOUNDARY
Content-Disposition: form-data; name='node_uid'
-----BOUNDARY


+ Response 200 (application/json)
    + Attributes (array[User])


# Group Log

## 日志列表 [/log/{?days,user,subject,summary}]

+ Parameters
    + days (number) - 距今天数，0特指当天
    + user (string) - 操作者
    + summary (string) - 事件信息
    + subject (string) - 事件类型，具体枚举值从 /meta/log/中获取，多选时以`|`间隔，形如 `a|b`

### 获取日志列表 [GET]

+ Response 200 (application/json)
    + Attributes (object)
        + count (number)
        + next (string)
        + previous (string)
        + results (array[LiteLog])

## 特定日志 [/log/{uuid}/]
+ Parameters
    + uuid (string) - 日志唯一标识

### 获取特定日志 [GET]
+ Response 200 (application/json)
    + Attributes (Log)

# Group Advanced

## crontab 插件 [/plugin/crontab/]

### 获取所有 crontab 插件 [GET]
+ Response 200 (application/json)
    + Attributes (array[CrontabPlugin])

## 特定 crontab 插件 [/plugin/crontab/{uuid}/]
+ Parameters
    + uuid (string) - 插件唯一标识

### 获取指定 crontab 插件 [GET]
+ Response 200 (application/json)
    + Attributes (CrontabPlugin)

### 修改指定 crontab 插件 [PATCH]
+ Requests JSON Message
    + Attributes
        + name
        + detail
        + schedule (string) - 形如 `* * * * *`
        + is_active (boolean)

+ Response 200 (application/json)
    + Attributes (CrontabPlugin)

## middleware 插件 [/plugin/middleware/]

### 获取所有 middleware 插件 [GET]
+ Response 200 (application/json)
    + Attributes (array[MiddlewarePlugin])

## 特定 middleware 插件 [/plugin/middleware/{uuid}/]
+ Parameters
    + uuid (string) - 插件唯一标识

### 获取指定 middleware 插件 [GET]
+ Response 200 (application/json)
    + Attributes (MiddlewarePlugin)

### 修改指定 middleware 插件 [PATCH]
+ Requests JSON Message
    + Attributes
        + name
        + detail
        + order_no (number)
        + is_active (boolean)

+ Response 200 (application/json)
    + Attributes (MiddlewarePlugin)

# SAML2 APP配置接口

## APP单点登录配置 [/saml/sso/redirect]

+ Request 302 Redirect
    + Attributes
        + SAMLRequest (string) - SP方SAML重定向请求

+ Response 302
    + Attributes
        + next (string) - 重定向未登录用户到oneid登录页

+ Response 302
    + Attributes
        + SAMLResponse (base64/string) - 检查用户COOKIES['spauthn']验证已登录，生成SAMLResponse加入url中重定向到SP方acs地址
            + Issuer - (string) IdP方处理元数据请求uri
            + Audience - (string) SP方监听SMALResponse的uri
            + entity - (string) IdP方获取元数据地址
            + status_code - (string) 登录状态
            + username - (string) IdP用户名
            + email - (string) IdP用户邮箱
            + private_email - (string) IdP用户私人邮箱
            + token - （string）IdP用户token

## SP获取元数据接口 [/saml/metadata/]

### 获取xml [GET]

+ Request JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes
        + metadata (string) - SAML2元数据显示在网页，用于SP方获取   FIXME: content-type

## 下载元数据文件 [/saml/download/metadata/]

### 下载 [GET]

+ Request JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes
        + metadata.xml (string) - IdP方新建时生成的元数据文件，用于在SP方配置时上传.  FIXME: content-type

# Group ThirdParty

## 钉钉扫码回调 [/ding/qr/callback/{?code,state}]
+ Parameters
    + code (string) - 钉钉扫码返回一次性查询码tmp_code
    + state (string) - 钉钉回调URL描述参数，一般固定为'STATE'

### 获取权限 [POST]
+ Requests JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 200 (application/json)
    + Attributes
        + token （string) - 未匹配用户，返回空字段token
        + third_party_id (string) - 返回钉钉id，用于下一步提交绑定

+ Response 400 (application/json)
    + Attributes
        + err_msg (string) - 'get dingding user time out'

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'ding qr not allowed'

+ Response 408 (application/json)
    + Attributes
        + err_msg (string) - 'get tmp code error'

## 查询用户 [/ding/query/user/]

### 查询未关联钉钉用户是否注册 [POST]
+ Requests JSON Message
    + Attributes
        + sms_token (string) - 通过返回的sms_token查询手机号，到用户表中查询对应的用户

+ Response 200 (application/json)
    + Attributes
        + exist (boolean) - 已注册返回True，未注册返回False

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'ding qr not allowed'

## 关联钉钉 [/ding/bind/]

### 绑定钉钉账号 [POST]
+ Request JSON Message
    + Attributes
        + user_id (string) - 钉钉用户扫码时查询返回的ding_id
        + sms_token (string) - 用户手机发短信后返回的sms_token

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'ding qr not allowed'

## 通过钉钉账号注册 [/ding/register/bind/]

### 钉钉用户注册+关联 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string) 
        + sms_token (string) - 绑定页面验证用户手机的sms_token
        + user_id (string) - 从钉钉查询的扫码用户的ding_id

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'ding qr not allowed'

## 支付宝扫码回调 [/alipay/qr/callback/{?auth_code}]
+ Parameters
    + auth_code (string) - 支付宝扫码返回一次性查询码auth_code

### 获取权限 [POST]
+ Requests JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 200 (application/json)
    + Attributes
        + token （string) - 未匹配用户，返回空字段token
        + third_party_id (string) - 返回支付宝user_id，用于下一步提交绑定

+ Response 400 (application/json)
    + Attributes
        + err_msg (string) - 'get alipay id error'

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'alipay qr not allowed'

## 关联支付宝 [/alipay/bind/]

### 绑定支付宝账号 [POST]
+ Request JSON Message
    + Attributes
        + user_id (string) - 支付宝用户扫码时查询返回的alipay_user_id
        + sms_token (string) - 用户手机发短信后返回的sms_token

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'alipay qr not allowed'

## 通过支付宝账号注册 [/alipay/register/bind/]

### 支付宝用户注册+关联 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string) 
        + sms_token (string) - 绑定页面验证用户手机的sms_token
        + user_id (string) - 从支付宝查询的扫码用户的alipay_user_id

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'alipay qr not allowed'

## 企业微信扫码回调 [/work_wechat/qr/callback/{?code}]
+ Parameters
    + code (string) - 企业微信扫码返回一次性查询码code

### 获取权限 [POST]
+ Requests JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 200 (application/json)
    + Attributes
        + token （string) - 未匹配用户，返回空字段token
        + third_party_id (string) - 返回企业微信user_id，用于下一步提交绑定

+ Response 400 (application/json)
    + Attributes
        + err_msg (string) - 'get work_wechat id error'

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'work_wechat qr not allowed'

## 关联企业微信 [/work_wechat/bind/]

### 绑定企业微信 [POST]
+ Request JSON Message
    + Attributes
        + user_id (string) - 企业微信用户扫码时查询返回的work_wechat_user_id
        + sms_token (string) - 用户手机发短信后返回的sms_token

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'work_wechat qr not allowed'

## 通过企业微信注册 [/work_wechat/register/bind/]

### 企业微信用户注册+关联 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string) 
        + sms_token (string) - 绑定页面验证用户手机的sms_token
        + user_id (string) - 从企业微信查询的扫码用户的work_wechat_user_id

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'work_wechat qr not allowed'

## 微信扫码回调 [/wechat/qr/callback/{?code}]
+ Parameters
    + code (string) - 微信扫码返回一次性查询码code

### 获取权限 [POST]
+ Requests JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 200 (application/json)
    + Attributes
        + token （string) - 未匹配用户，返回空字段token
        + third_party_id (string) - 返回微信unionid，用于下一步提交绑定

+ Response 400 (application/json)
    + Attributes
        + err_msg (string) - 'get wechat id error'

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'wechat qr not allowed' 

## 关联微信 [/wechat/bind/]

### 绑定微信账号 [POST]
+ Request JSON Message
    + Attributes
        + user_id (string) - 微信用户扫码时查询返回的unionid
        + sms_token (string) - 用户手机发短信后返回的sms_token

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'wechat qr not allowed'

## 通过微信注册 [/wechat/register/bind/]

### 微信用户注册+关联 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string) 
        + sms_token (string) - 绑定页面验证用户手机的sms_token
        + user_id (string) - 从微信查询的扫码用户的unionid

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'wechat qr not allowed'

## QQ扫码回调 [/qq/qr/callback/{?code}]
+ Parameters
    + code (string) - qq扫码返回一次性查询码code

### 获取权限 [POST]
+ Requests JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 200 (application/json)
    + Attributes
        + token （string) - 未匹配用户，返回空字段token
        + third_party_id (string) - 返回openid，用于下一步提交绑定

+ Response 400 (application/json)
    + Attributes
        + err_msg (string) - 'get qq id error'

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'qq qr not allowed' 

## 关联QQ [/qq/bind/]

### 绑定QQ账号 [POST]
+ Request JSON Message
    + Attributes
        + user_id (string) - qq用户扫码时查询返回的openid
        + sms_token (string) - 用户手机发短信后返回的sms_token

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'qq qr not allowed'

## 通过QQ注册 [/qq/register/bind/]

### QQ用户注册+关联 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string) 
        + sms_token (string) - 绑定页面验证用户手机的sms_token
        + user_id (string) - 从qq查询的扫码用户的openid

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'work_qq qr not allowed'

## Github账号登录回调 [/github/callback/{?code}]
+ Parameters
    + code (string) - github登录返回一次性查询码code

### 获取权限 [POST]
+ Requests JSON Message
    + Attributes

+ Response 200 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 200 (application/json)
    + Attributes
        + token （string) - 未匹配用户，返回空字段token
        + third_party_id (string) - 返回github_user_id，用于下一步提交绑定

+ Response 400 (application/json)
    + Attributes
        + err_msg (string) - 'get github id error'

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'github not allowed' 

## 关联Github [/github/bind/]

### 绑定Github账号 [POST]
+ Request JSON Message
    + Attributes
        + user_id (string) - github用户登录时查询返回的id
        + sms_token (string) - 用户手机发短信后返回的sms_token

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'github not allowed'

## 通过Github账号注册 [/github/register/bind/]

### Github用户注册+关联 [POST]
+ Request JSON Message
    + Attributes
        + username (string)
        + password (string) 
        + sms_token (string) - 绑定页面验证用户手机的sms_token
        + user_id (string) - 从github查询的用户的id

+ Response 201 (application/json)
    + Attributes (UserWithPermWithToken)

+ Response 403 (application/json)
    + Attributes
        + err_msg (string) - 'github not allowed'
