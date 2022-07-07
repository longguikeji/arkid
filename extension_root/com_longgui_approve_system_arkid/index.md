# 默认审批系统插件

## 功能介绍
默认审批系统插件安装后，会在**审批管理**菜单下面添加**默认请求处理**页面，用于处理分配给当前审批系统的审批请求

### 创建审批动作
=== "打开审批动作页面，点击创建按钮"
    [![X7nDTH.png](https://s1.ax1x.com/2022/06/16/X7nDTH.png)](https://imgtu.com/i/X7nDTH)

=== "填入表单参数"
    [![X45oyq.png](https://s1.ax1x.com/2022/06/14/X45oyq.png)](https://imgtu.com/i/X45oyq)


### 生成审批请求

=== "打开账号生命周期，点击创建按钮"
    [![X7nulV.png](https://s1.ax1x.com/2022/06/16/X7nulV.png)](https://imgtu.com/i/X7nulV)

=== "配置表单参数，点击创建按钮"
    由于上个步骤中已经配置了针对创建生命周期配置的审批动作，所以该请求返回403
    [![X59seS.png](https://s1.ax1x.com/2022/06/14/X59seS.png)](https://imgtu.com/i/X59seS)


### 查看审批请求

=== "打开**审批管理->审批请求**页面"
    [![X5Pr5Q.png](https://s1.ax1x.com/2022/06/14/X5Pr5Q.png)](https://imgtu.com/i/X5Pr5Q)


=== "打开**用户头像->审批请求**页面"
    [![X5PDUg.png](https://s1.ax1x.com/2022/06/14/X5PDUg.png)](https://imgtu.com/i/X5PDUg)


### 处理审批请求

=== "打开**审批管理->默认请求处理**页面， 点击通过按钮"
    [![X5nksH.png](https://s1.ax1x.com/2022/06/14/X5nksH.png)](https://imgtu.com/i/X5nksH)


=== "打开**已审核**页签， 确认状态已改变"
    [![X5nFQe.png](https://s1.ax1x.com/2022/06/14/X5nFQe.png)](https://imgtu.com/i/X5nFQe)


=== "打开**账号生命周期**页面， 确认待审核的请求重新执行"
    [![X5nPzD.png](https://s1.ax1x.com/2022/06/14/X5nPzD.png)](https://imgtu.com/i/X5nPzD)

    

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