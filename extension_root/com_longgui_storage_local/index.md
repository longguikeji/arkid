# 静态文件存储插件：本地文件存储

## 功能介绍

实现静态文件的本地化存储，存储路径默认为{workspace}/storage/

* 注意： 此为平台插件，需要平台管理员权限进行配置

## 配置指南

=== "插件租赁"

经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到本地文件存储插件卡片，点击租赁

[![vELyVS.png](https://s1.ax1x.com/2022/08/02/vELyVS.png)](https://imgtu.com/i/vELyVS)

=== "平台配置"

经由左侧菜单栏依次进入【平台管理】->【平台插件】, 在已安装页面找到本地文件存储插件卡片，点击插件配置，配置文件存储路径

[![vELXx1.png](https://s1.ax1x.com/2022/08/02/vELXx1.png)](https://imgtu.com/i/vELXx1)

[![vVD6iQ.md.png](https://s1.ax1x.com/2022/08/03/vVD6iQ.md.png)](https://imgtu.com/i/vVD6iQ)

## 实现思路

开发者在开发静态文件存储插件时，需继承StorageExtension,并重载save_file和resolve方法即可

## 抽象方法实现

* [load](#extension_root.com_longgui_storage_local.LocalStorageExtension.load)
* [save_file](#extension_root.com_longgui_storage_local.LocalStorageExtension.save_file)
* [resolve](#extension_root.com_longgui_storage_local.LocalStorageExtension.resolve)

## 代码

::: extension_root.com_longgui_storage_local.LocalStorageExtension
    rendering:
        show_source: true