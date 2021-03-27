ArkID - v2

**DO NOT USE THIS VRESION IN PRODUCTION (请勿在生产环境中使用)**

## TODO

1. 通过扩展实现External idP的授权登陆
   1. [ ] 钉钉
   2. [x] Gitee
   3. [x] Github
2. 通过扩展实现tenant isolate, scope支持global, tenant
3. 通过扩展实现同步功能
   1. [ ] SCIM(从core中挪出来)
   2. [ ] LDAP
4. 通过扩展实现Storage Provider
   1. [ ] 本地文件系统
   2. [ ] 七牛
   3. [ ] OSS
   4. [ ] Minio
5. 通过扩展实现MFA
   1. [ ] Captcha
   2. [ ] HOTP/TOTP
   3. [ ] SMS
   4. [ ] Email
6. 通过扩展实现协议支持
   1. [x] OAuth2
   2. [x] OIDC
   3. [ ] LDAP
   4. [ ] SAML
   5. [ ] CAS WEB
7. 通过扩展实现Token 基础框架以及扩展实现Token扩展
8. User & Group Model的扩展
9.  ArkID Core Package化
10. 扩展的DB Model 以及 依赖隔离支持


## arkid cli命令

### create-extension

### list-extension

### start

### reload

### stop


## 角色划分

1. Global Administrator(全局管理员) 跨租户管理
2. Tenant Administrator(租户管理员)