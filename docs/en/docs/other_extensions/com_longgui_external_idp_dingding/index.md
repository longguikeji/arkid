# Dingding 第三方登录插件

## 功能介绍
配置Dingding插件后，可以点击ArkID登录页面的Dingding图标，跳转到Dingding网站完成Oauth2认证，并和ArkID的用户绑定

### 首先成为钉钉开发者
    详情请参考[成为钉钉开发者](https://open.dingtalk.com/document/org/become-a-dingtalk-developer)
    配置钉钉应用请参考链接[实现登录第三方网站](https://open.dingtalk.com/document/orgapp-server/tutorial-obtaining-user-personal-information)

### 登录钉钉开发者后台，创建并配置应用

=== "点击创建应用"
    [![jzIFGn.png](https://s1.ax1x.com/2022/07/26/jzIFGn.png)](https://imgtu.com/i/jzIFGn)

=== "填写表单参数"
    [![jzIaIH.png](https://s1.ax1x.com/2022/07/26/jzIaIH.png)](https://imgtu.com/i/jzIaIH)

=== "保存App Key和App Secret"
    [![jzoSQx.png](https://s1.ax1x.com/2022/07/26/jzoSQx.png)](https://imgtu.com/i/jzoSQx)

=== "配置开发管理信息"
    [![jzo07F.png](https://s1.ax1x.com/2022/07/26/jzo07F.png)](https://imgtu.com/i/jzo07F)

=== "添加接口权限"
    [![jzo79A.png](https://s1.ax1x.com/2022/07/26/jzo79A.png)](https://imgtu.com/i/jzo79A)

### 创建ArkID第三方登录配置,获取回调URL

=== "创建钉钉第三方登录"
    [![jz7ZsP.png](https://s1.ax1x.com/2022/07/26/jz7ZsP.png)](https://imgtu.com/i/jz7ZsP)

=== "点击编辑按钮，获取ArkID回调URL"
    [![jz7sQ1.png](https://s1.ax1x.com/2022/07/26/jz7sQ1.png)](https://imgtu.com/i/jz7sQ1)

### 更新钉钉应用回调URL，点击登录按钮

=== "设置钉钉应用回调URL"
    [![jzH8te.png](https://s1.ax1x.com/2022/07/26/jzH8te.png)](https://imgtu.com/i/jzH8te)


=== "点击登录页面钉钉图标"
    [![jzLgcd.png](https://s1.ax1x.com/2022/07/26/jzLgcd.png)](https://imgtu.com/i/jzLgcd)

=== "钉钉扫码登录"
    [![jzLIN8.png](https://s1.ax1x.com/2022/07/26/jzLIN8.png)](https://imgtu.com/i/jzLIN8)

# 统一绑定和解绑说明
请参见[三方账号绑定](/%20%20%20用户指南/用户手册/%20普通用户/认证管理/三方账号绑定/)