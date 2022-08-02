# 短信插件：阿里云短信

## 功能介绍

为平台提供短信服务支持，短信服务商为阿里云短信。

## 配置指南

=== "插件租赁"

经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到阿里云短信插件卡片，点击租赁

[![vEsZzn.png](https://s1.ax1x.com/2022/08/02/vEsZzn.png)](https://imgtu.com/i/vEsZzn)

=== "插件租户配置"

租赁完成后，进入已租赁列表，找到阿里云短信插件卡片，点击租户配置，配置相关数据

[![vEsDFe.md.png](https://s1.ax1x.com/2022/08/02/vEsDFe.md.png)](https://imgtu.com/i/vEsDFe)

=== "插件运行时配置"

租户配置完成后回到已租赁页面，在阿里云短信插件卡片上点击运行时配置，在弹出窗口中点击新建，输入对应的短信模板配置即可

[![vEyZkD.md.png](https://s1.ax1x.com/2022/08/02/vEyZkD.md.png)](https://imgtu.com/i/vEyZkD)

[![vEych4.md.png](https://s1.ax1x.com/2022/08/02/vEych4.md.png)](https://imgtu.com/i/vEych4)

* 注意： 模板参数一项中如不填则默认为["code"]，适用于短信验证码

## 抽象方法实现
* [load](#extension_root.com_longgui_sms_aliyun.AliyunSMSExtension.load)
* [send_sms](#extension_root.com_longgui_sms_aliyun.AliyunSMSExtension.send_sms)

## 代码

::: extension_root.com_longgui_sms_aliyun.AliyunSMSExtension
    rendering:
        show_source: true