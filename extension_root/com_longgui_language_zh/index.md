# 多语言包插件：简体中文

## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到中文语言包插件卡片，点击租赁
    [![vEqtlq.png](https://s1.ax1x.com/2022/08/02/vEqtlq.png)](https://imgtu.com/i/vEqtlq)

=== "语言包数据更新"
    * 系统提供语言包数据在线更新能力，优先级为 用户更新语言包数据 > 语言包插件数据 > 系统默认语言翻译
    + 经由左侧菜单栏依次进入【平台管理】->【语言包管理】，进入语言包列表页面
    [![vEqohd.md.png](https://s1.ax1x.com/2022/08/02/vEqohd.md.png)](https://imgtu.com/i/vEqohd)
    + 点击语言包行右侧的编辑按钮，进入语言包数据详情页面
    [![vEqqjP.md.png](https://s1.ax1x.com/2022/08/02/vEqqjP.md.png)](https://imgtu.com/i/vEqqjP)
    + 点击右上角新增按钮，进入新增翻译页面，此处原词句是指系统中待翻译的词句，译词句则为翻译后的词句
    [![vEL99s.md.png](https://s1.ax1x.com/2022/08/02/vEL99s.md.png)](https://imgtu.com/i/vEL99s)

## 抽象方法实现
* [language_type](#extension_root.com_longgui_language_zh.TranslationZhExtension.language_type)
* [language_data](#extension_root.com_longgui_sms_aliyun.TranslationZhExtension.language_data)

## 代码

::: extension_root.com_longgui_language_zh.TranslationZhExtension
    rendering:
        show_source: true