# ArkID 用户数据同步插件

## 功能介绍
1. Server模式实现了可以通过标准SCIM接口获取ArkID中的用户和组织
2. Client模式实现了可以通过定时任务拉取SCIM Server中的用户和组织

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