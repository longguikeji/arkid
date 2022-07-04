# 默认生命周期插件

## 功能介绍
设置用户过期时间后，定时任务会定期将用户过期时间和当前时间作比较，如果当前时间大于用户过期时间，则禁用该用户

### 配置生命周期定时任务

=== "打开账号生命周期页面"
    点击**编辑生命周期定时任务**按钮
    [![X7mszV.png](https://s1.ax1x.com/2022/06/16/X7mszV.png)](https://imgtu.com/i/X7mszV)

=== "配置定时任务表单参数"
    其中定时运行时间语法参考**linux Crontab**命令语法，以下图为例：每天8点运行一次，如果失败再每隔间隔30秒重试2次
    [![X4Jmsf.png](https://s1.ax1x.com/2022/06/14/X4Jmsf.png)](https://imgtu.com/i/X4Jmsf)


### 配置用户过期时间


=== "点击创建按钮"
    [![X7nulV.png](https://s1.ax1x.com/2022/06/16/X7nulV.png)](https://imgtu.com/i/X7nulV)

=== "点击Config"
    [![X7nGk9.png](https://s1.ax1x.com/2022/06/16/X7nGk9.png)](https://imgtu.com/i/X7nGk9)

=== "配置用户和过期时间"
    [![X4ye4P.png](https://s1.ax1x.com/2022/06/14/X4ye4P.png)](https://imgtu.com/i/X4ye4P)

=== "配置完成后，点击创建按钮"
    [![X4yn9f.png](https://s1.ax1x.com/2022/06/14/X4yn9f.png)](https://imgtu.com/i/X4yn9f)

## 实现思路
定时任务将用户的过期时间和当前时间作比较，如果用户已经过期，则设置用户属性is_active为False，将禁止该用户登录ArkID</br>
需要覆盖插件基类的抽象方法，插件基类见[arkid.core.extension.account_life.AccountLifeExtension](/%20%20开发者指南/%20插件分类/账户生命周期/)

## 抽象方法实现:
* [periodic_task](#extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension.periodic_task)


## 代码

::: extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension
    rendering:
        show_source: true