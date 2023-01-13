# AD 用户数据同步插件

## 功能介绍
1. Server模式实现了可以通过标准SCIM接口获取AD或者openldap中的用户和组织
2. Client模式实现了可以通过定时任务拉取AD或者openldap中的用户和组织
3. 下文以openldap说明如何配置与ArkID之间的数据同步


### 配置Openldap同步数据到ArkID

=== "安装插件"

    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到AD用户数据同步卡片，点击租赁<br/>

    [![BO1nRB.png](https://v1.ax1x.com/2022/12/14/BO1nRB.png)](https://zimgs.com/i/BO1nRB)

=== "配置Openldap作为数据源服务器"
    [![BO1IFt.png](https://v1.ax1x.com/2022/12/14/BO1IFt.png)](https://zimgs.com/i/BO1IFt)

=== "配置ArkID作为数据同步Client"
    [![BO1fqb.png](https://v1.ax1x.com/2022/12/14/BO1fqb.png)](https://zimgs.com/i/BO1fqb)

=== "查看Openldap中源数据"
    
    [![BO1iae.png](https://v1.ax1x.com/2022/12/14/BO1iae.png)](https://zimgs.com/i/BO1iae)

=== "验证数据已经同步到ArkID"

    [![BO1sMP.png](https://v1.ax1x.com/2022/12/14/BO1sMP.png)](https://zimgs.com/i/BO1sMP)


!!! 提示
    openldap作为数据源只会返回目标组织DN下特定objectClass的数据，用户为:inetOrgPerson，组织为:organizationalUnit

### 配置从ArkID同步数据到Openldap

=== "安装插件"

    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到AD用户数据同步卡片，点击租赁<br/>

    [![BO1nRB.png](https://v1.ax1x.com/2022/12/14/BO1nRB.png)](https://zimgs.com/i/BO1nRB)

=== "配置ArkID作为数据同步源服务器"

    [![BO163w.png](https://v1.ax1x.com/2022/12/14/BO163w.png)](https://zimgs.com/i/BO163w)

=== "配置Openldap作为数据同步Client"

    [![BO1ZCO.png](https://v1.ax1x.com/2022/12/14/BO1ZCO.png)](https://zimgs.com/i/BO1ZCO)

=== "配置Openldap Client属性映射"
    
    [![BO1F56.png](https://v1.ax1x.com/2022/12/14/BO1F56.png)](https://zimgs.com/i/BO1F56)

    !!! 提示
        openldap创建的用户的objectClass为:inetOrgPerson，组织的objectClass为:organizationalUnit,
        用户必需属性为sn,cn，保证数据映射中有这两个，添加其他的属性映射前请参考对应的schema中是否存在对应属性
        

=== "查看ArkID中源数据"
    
    [![BO1eBQ.png](https://v1.ax1x.com/2022/12/14/BO1eBQ.png)](https://zimgs.com/i/BO1eBQ)

=== "验证数据已经同步到Openldap"
    
    [![BO1obf.png](https://v1.ax1x.com/2022/12/14/BO1obf.png)](https://zimgs.com/i/BO1obf)
