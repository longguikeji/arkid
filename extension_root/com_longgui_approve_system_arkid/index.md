# 默认审批系统插件

## 功能介绍
默认审批系统插件安装后，会在**审批管理**菜单下面添加**默认请求处理**页面，用于处理分配给当前审批系统的审批请求

1. 打开**审批管理->审批动作**页面，点击创建按钮，选择请求路径，请求方法和处理审批请求的审批系统，如下图

    [![X45oyq.png](https://s1.ax1x.com/2022/06/14/X45oyq.png)](https://imgtu.com/i/X45oyq)

2. 打开**用户管理->账号生命周期**菜单, 点击创建按钮，创建生命周期配置，由于上个步骤中已经配置了针对创建生命周期配置的审批动作，所以该请求返回403，如下图

    [![X59seS.png](https://s1.ax1x.com/2022/06/14/X59seS.png)](https://imgtu.com/i/X59seS)

3. 继上个步骤后，在**审批管理->审批请求**页面, 以及点击系统右上角用户头像弹出的**审批请求**页面，会显示一条新的审批请求记录，状态为waiting，</br>
这两个页面一个是显示系统所有审批请求，一个显示用户自己的审批请求，如下图

    [![X5Pr5Q.png](https://s1.ax1x.com/2022/06/14/X5Pr5Q.png)](https://imgtu.com/i/X5Pr5Q)
    [![X5PDUg.png](https://s1.ax1x.com/2022/06/14/X5PDUg.png)](https://imgtu.com/i/X5PDUg)

4. 同时**审批管理->默认请求处理**页面也会显示一条新增的审批请求，这个页面主要用于系统管理员处理（通过或者拒绝）审批请求，</br>
如果点击通过，审批请求状态会改变，存储在该审批请求中的创建生命周期配置的逻辑也会在此时重新执行，因此打开**用户管理->账号生命周期**菜单，</br>
会显示一条新增的账号生命周期配置，如下图

    [![X5nksH.png](https://s1.ax1x.com/2022/06/14/X5nksH.png)](https://imgtu.com/i/X5nksH)
    [![X5nFQe.png](https://s1.ax1x.com/2022/06/14/X5nFQe.png)](https://imgtu.com/i/X5nFQe)
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