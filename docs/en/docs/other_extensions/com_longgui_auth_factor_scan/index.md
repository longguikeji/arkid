# 扫码认证因素
## 功能介绍
通过在已经登录ArkID设备上，调用摄像头扫描另外一台设备上的登录二维码，实现免账号密码的快捷登录

## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到扫码认证因素插件卡片，点击租赁<br/>
    [![BVuqMc.png](https://v1.ax1x.com/2022/11/23/BVuqMc.png)](https://zimgs.com/i/BVuqMc)

=== "认证因素配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证因素】,点击创建按钮，类型选择"Scan",填入相关信息，至此配置完成<br/>
    [![BVuw33.png](https://v1.ax1x.com/2022/11/23/BVuw33.png)](https://zimgs.com/i/BVuw33)

=== "打开PC登录界面"
    [![BVuy5j.png](https://v1.ax1x.com/2022/11/23/BVuy5j.png)](https://zimgs.com/i/BVuy5j)

=== "手机打开【我的】->【认证管理】->【扫码登录】,点击开始扫描按钮"
    [![BVuHC5.png](https://v1.ax1x.com/2022/11/23/BVuHC5.png)](https://zimgs.com/i/BVuHC5)

=== "扫描二维码"
    [![BVb8vO.png](https://v1.ax1x.com/2022/11/23/BVb8vO.png)](https://zimgs.com/i/BVb8vO)

=== "确认登录"
    [![BV8CPj.png](https://v1.ax1x.com/2022/11/23/BV8CPj.png)](https://zimgs.com/i/BV8CPj)

!!! 注意
    chrome浏览器访问http网站默认没有访问摄像头的权限，需要手工设置参数(Insecure origins treated as secure)后才可以
