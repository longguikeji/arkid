# 静态文件存储插件：本地文件存储

## 功能介绍

实现静态文件的本地化存储，存储路径默认为{workspace}/storage/

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