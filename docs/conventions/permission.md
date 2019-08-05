# 权限设计

## naming conventions

由三部分构成
- subject (namespace)
- scope
- action

各部分由小写字母、数字和`-`构成，以`_`顺序连接构成 perm_uid，全局唯一。形如`app_demo_access`

### subject
有限个，全部内部指定，不可随意新增。目前有以下几项：

- app   
专指应用( APP )权限。

- system  
专指 OneID 内置权限。

### scope
操作范围，对于应用权限而言，此处为应用UID

### action
操作行为  
每个应用至少有一个 `access` 权限   
应用内新建权限时，该字段随机生成


## buildin permission

- `system_user_create`  
创建用户

- `system_category_create`  
创建大类

- `system_app_create`  
创建应用

- `system_log_read`
查看日志

- `system_config_write`
公司配置、基础设施配置

- `system_account_sync`
账号同步
