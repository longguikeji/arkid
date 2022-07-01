# ArkID 用户数据同步插件

## 功能介绍
1. Server模式实现了可以通过标准SCIM接口获取ArkID中的用户和组织
2. Client模式实现了可以通过定时任务拉取SCIM Server中的用户和组织

### 启动Celery Worker和Beat


=== "启动Celery Worker"
    [![X7bnCq.png](https://s1.ax1x.com/2022/06/16/X7bnCq.png)](https://imgtu.com/i/X7bnCq)

=== "启动Celery Beat"
    [![X7bK2V.png](https://s1.ax1x.com/2022/06/16/X7bK2V.png)](https://imgtu.com/i/X7bK2V)

### 创建ArkID 同步Server

=== "打开**身份认证源->SCIM数据同步**页面， 点击创建"
    [![X7bu80.png](https://s1.ax1x.com/2022/06/16/X7bu80.png)](https://imgtu.com/i/X7bu80)

=== "配置表单参数"
    [![X7Xg0S.png](https://s1.ax1x.com/2022/06/16/X7Xg0S.png)](https://imgtu.com/i/X7Xg0S)

### 创建ArkID 同步Client

=== "打开**身份认证源->SCIM数据同步**页面"
    点击创建
    [![X7bu80.png](https://s1.ax1x.com/2022/06/16/X7bu80.png)](https://imgtu.com/i/X7bu80)

=== "配置表单参数"
    以下配置表示定时同步任务每10分钟运行一次
    [![X7qhf1.png](https://s1.ax1x.com/2022/06/16/X7qhf1.png)](https://imgtu.com/i/X7qhf1)

### 确认Celery Beat更新，Celery Worker运

=== "确认Celery Beat定时任务更新"
    [![X7qz1P.png](https://s1.ax1x.com/2022/06/16/X7qz1P.png)](https://imgtu.com/i/X7qz1P)


=== "确认Celery Workder任务执行"
    [![X7XSeS.png](https://s1.ax1x.com/2022/06/16/X7XSeS.png)](https://imgtu.com/i/X7XSeS)

## 实现思路
需要覆盖插件基类的抽象方法，插件基类见[arkid.core.extension.scim_sync.ScimSyncExtension](/%20%20开发者指南/%20插件分类/数据同步/)

## 抽象方法实现:
#### Server模式的抽象方法
* [query_users](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.query_users)
* [query_groups](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.query_groups)
#### Client模式的抽象方法
* [sync_groups](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.sync_groups)
* [sync_users](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.sync_users)

## 代码

::: extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension
    rendering:
        show_source: true