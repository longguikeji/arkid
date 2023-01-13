# LDAP 认证因素插件

## 功能介绍

ldap认证因素插件，使用LDAP协议来完成用户绑定以及认证

## 使用示例

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到LDAP认证因素插件卡片，点击租赁<br/>

=== "添加认证因素"
    [![vprGNV.md.png](https://s1.ax1x.com/2022/07/27/vprGNV.md.png)](https://imgtu.com/i/vprGNV)
    
=== "登录页面"
    [![vproUP.md.png](https://s1.ax1x.com/2022/07/27/vproUP.md.png)](https://imgtu.com/i/vproUP)<br/>
    注意：用户信息字段映射中字段名为arkid平台中USER模型属性字段名称，映射名为在LDAP协议中用户信息属性字段名称，该映射关系配置后会将认证过程中获取的用户信息对应写入arkid数据库
