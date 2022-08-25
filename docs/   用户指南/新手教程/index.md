# 新手教程

以下介绍一个新手管理员的成长之路

!!! 准备工作

    在SaaS系统中创建租户，或者私有化部署后用admin账户登录后，就可以继续以下操作
## 添加第一个OIDC应用

=== "打开应用列表"

    [![X40bd0.jpg](https://s1.ax1x.com/2022/06/14/X40bd0.jpg)](https://imgtu.com/i/X40bd0)

=== "点击创建，填写表单"

    点击确认后，对话框关闭，可以看到你创建的应用。

    [![XhxYWV.jpg](https://s1.ax1x.com/2022/06/14/XhxYWV.jpg)](https://imgtu.com/i/XhxYWV)

=== "点击协议配置"

    [![XhxBw9.jpg](https://s1.ax1x.com/2022/06/14/XhxBw9.jpg)](https://imgtu.com/i/XhxBw9)

=== "填写配置"
    应用类型选择为OIDC，填写参数，创建完毕

    [![XhxyJx.jpg](https://s1.ax1x.com/2022/06/14/XhxyJx.jpg)](https://imgtu.com/i/XhxyJx)

=== "再次点击协议配置"
    即可查看该协议所有相关的参数。
    
    相关参数的含义，请参考[OIDC插件的文档](/%20系统插件/com_longgui_app_protocol_oidc/)

    [![Xhx5TA.jpg](https://s1.ax1x.com/2022/06/14/Xhx5TA.jpg)](https://imgtu.com/i/Xhx5TA)



## 添加一个新的账号
=== "打开用户列表"

    [![X4BBkV.jpg](https://s1.ax1x.com/2022/06/14/X4BBkV.jpg)](https://imgtu.com/i/X4BBkV)

=== "点击创建"
    填写下面的表单，点击创建即可。

    [![X4BrfU.jpg](https://s1.ax1x.com/2022/06/14/X4BrfU.jpg)](https://imgtu.com/i/X4BrfU)




## 添加组织结构或角色

=== "打开用户分组"
    关于分组的详细介绍可以看 [用户管理-用户分组](/%20%20%20用户指南/用户手册/%20租户管理员/%20%20%20%20%20用户管理/#_3)

    [![X4TpdK.jpg](https://s1.ax1x.com/2022/06/14/X4TpdK.jpg)](https://imgtu.com/i/X4TpdK)

=== "点击创建"
    填写下面的表单，点击创建即可。

    [![X4Tndf.jpg](https://s1.ax1x.com/2022/06/14/X4Tndf.jpg)](https://imgtu.com/i/X4Tndf)

=== "为分组添加用户"

    [![X4TGyn.jpg](https://s1.ax1x.com/2022/06/14/X4TGyn.jpg)](https://imgtu.com/i/X4TGyn)

=== "选择用户"

    [![X4T0W4.jpg](https://s1.ax1x.com/2022/06/14/X4T0W4.jpg)](https://imgtu.com/i/X4T0W4)

## 为目标账号开通一个应用


## 为目标组织结构开通一组权限
## 添加手机验证码作为新的认证因素

=== "打开认证因素"

    [![X4Tndf.jpg](https://s1.ax1x.com/2022/06/14/X4Tndf.jpg)](https://imgtu.com/i/X4Tndf)

=== "点击创建"

    选择认证因素类型“mobile”，填写表单


=== "打开认证因素"


## AD与ArkID的数据同步

配置同步AD中的用户和组织到ArkID

=== "打开SCIM数据同步，点击创建"

    [![vgGHo9.png](https://s1.ax1x.com/2022/08/24/vgGHo9.png)](https://imgse.com/i/vgGHo9)

=== "配置AD同步Server"

    [![vgYMnO.png](https://s1.ax1x.com/2022/08/24/vgYMnO.png)](https://imgse.com/i/vgYMnO)

=== "配置ArkID同步Client"

    !!! 提示
        SCIM同步服务器: 选择上个步骤创建的 AD同步Server</br>
        定时运行时间: 格式参照linux crontab, 下图中表示每天11：51运行定时同步任务
        定时任务需要启动celery work和beat:</br>
        celery -A arkid.core.tasks.celery beat -l debug</br>
        celery -A arkid.core.tasks.celery worker -l debug

    [![vgY3AH.png](https://s1.ax1x.com/2022/08/24/vgY3AH.png)](https://imgse.com/i/vgY3AH)

=== "查看AD中源数据"
    
    [![vgYfDU.png](https://s1.ax1x.com/2022/08/24/vgYfDU.png)](https://imgse.com/i/vgYfDU)

=== "查看ArkID中已同步数据"
    
    [![vgYIUJ.png](https://s1.ax1x.com/2022/08/24/vgYIUJ.png)](https://imgse.com/i/vgYIUJ)

## 启用多租户，成为IDaaS
