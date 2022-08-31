# ArkID 用户数据同步插件

## 功能介绍
1. Server模式实现了可以通过标准SCIM接口获取ArkID中的用户和组织
2. Client模式实现了可以通过定时任务拉取SCIM Server中的用户和组织


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


## 实现思路
需要覆盖插件基类的抽象方法，插件基类见[arkid.core.extension.scim_sync.ScimSyncExtension](../../%20%20开发者指南/%20插件分类/数据同步/)

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
