# 默认生命周期插件

## 功能介绍
设置用户过期时间后，定时任务会定期将用户过期时间和当前时间作比较，如果当前时间大于用户过期时间，则禁用该用户

## 实现思路
需要覆盖插件基类的抽象方法，插件基类见[arkid.core.extension.account_life.AccountLifeExtension](/%20%20开发者指南/%20插件分类/账户生命周期/)

## 抽象方法实现:
* [periodic_task](#extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension.periodic_task)


## 代码

::: extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension
    rendering:
        show_source: true