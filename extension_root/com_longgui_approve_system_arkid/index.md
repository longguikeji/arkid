# 默认审批系统插件

## 功能介绍
默认审批系统插件安装后，会在**审批管理**菜单下面添加**默认请求处理**页面，用于处理分配给当前审批系统的审批请求

## 实现思路
- 在**approve_requests_page**中添加**默认请求处理**页面
- 在views中添加改变ApproveRequest状态的接口
- 由于此插件只不需要将审批请求发送到第三方所以没有覆盖抽象方法[create_approve_request](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.create_approve_request)
- 由于此插件添加了默认请求处理页面，并且在默认请求处理页面中调用views中的方法改变审批请求状态，所以没有覆盖抽象方法[change_approve_request_status](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.change_approve_request_status)
- 插件基类见[arkid.core.extension.extrnal_idp.ExternalIdpExtension](/%20%20开发者指南/%20插件分类/数据同步/)

## 抽象方法实现:
* [change_approve_request_status](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.change_approve_request_status)
* [create_approve_request](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.create_approve_request)



## 代码

::: extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension
    rendering:
        show_source: true