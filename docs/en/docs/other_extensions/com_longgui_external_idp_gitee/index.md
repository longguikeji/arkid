# Gitee 第三方登录插件

## 功能介绍
配置Gitee插件后，可以点击ArkID登录页面的Gitee图标，跳转到Gitee网站完成Oauth2认证，并和ArkID的用户绑定

### 创建Gitee应用

=== "打开创建应用页面"
    [![jzj69U.md.jpg](https://s1.ax1x.com/2022/07/26/jzj69U.md.jpg)](https://imgtu.com/i/jzj69U)

=== "点击创建应用，填写表单(名称，主页URL和回调URL可以随意填写，回调URL后面步骤中会更改成ArkID自动生成的URL)"
    [![jzjfBR.md.jpg](https://s1.ax1x.com/2022/07/26/jzjfBR.md.jpg)](https://imgtu.com/i/jzjfBR)

=== "保存Client ID和Client Secret"
    [![jzjIN6.md.jpg](https://s1.ax1x.com/2022/07/26/jzjIN6.md.jpg)](https://imgtu.com/i/jzjIN6)

### 创建ArkID第三方登录配置,获取回调URL

=== "打开第三方认证页面"
    [![jzjOud.md.jpg](https://s1.ax1x.com/2022/07/26/jzjOud.md.jpg)](https://imgtu.com/i/jzjOud)

=== "填写表单参数， 点击创建"
    [![jzvS4f.md.jpg](https://s1.ax1x.com/2022/07/26/jzvS4f.md.jpg)](https://imgtu.com/i/jzvS4f)

=== "点击编辑按钮，获取ArkID回调URL"
    [![jzvPgg.md.jpg](https://s1.ax1x.com/2022/07/26/jzvPgg.md.jpg)](https://imgtu.com/i/jzvPgg)

### 更新Gitee应用回调URL，点击登录按钮

=== "重新设置Gitee应用回调URL"
    [![jzvkuj.md.jpg](https://s1.ax1x.com/2022/07/26/jzvkuj.md.jpg)](https://imgtu.com/i/jzvkuj)

=== "点击登录页面Gitee图标"
    [![jzvuCT.md.jpg](https://s1.ax1x.com/2022/07/26/jzvuCT.md.jpg)](https://imgtu.com/i/jzvuCT)

=== "点击认证按钮"
    [![jzvt56.md.jpg](https://s1.ax1x.com/2022/07/26/jzvt56.md.jpg)](https://imgtu.com/i/jzvt56)

# 统一绑定和解绑说明
请参见[三方账号绑定](/%20%20%20用户指南/用户手册/%20普通用户/认证管理/三方账号绑定/)