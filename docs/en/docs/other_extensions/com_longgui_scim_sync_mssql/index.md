# SQL Server 用户数据同步插件

## 功能介绍
1. Server模式实现了可以通过标准SCIM接口获取SQL Server数据库中的用户和组织
2. Client模式实现了可以通过定时任务拉取SCIM Server中的用户和组织, 同步到SQL Server数据库中

## 配置两个SQL Server数据库之间数据库同步

### 创建两个数据库和表

- 创建作为提供同步数据的Server数据库，建立**users**, **groups**表， 以及user所属groups的中间表**users_groups**, </br>
**users_groups**中间表中user_id外键关联users(id)， group_id外键关联groups(id)
    
    !!! 提示
        此例中演示user和group之间是ManyToMany的关系, 如果user只属于一个group，可以在**users**表中定义group_id，外键关联groups(id)

- 创建Client数据库，用于将Server数据库提供的数据同步到Client数据库

    !!! 注意
        为演示方便，Client数据库中的表定义和Server数据库一样,实际生产环境中可能不同

### 配置SQL Server 源数据库

=== "打开**SCIM数据同步**页面，点击创建"
    [![vgGHo9.png](https://s1.ax1x.com/2022/08/24/vgGHo9.png)](https://imgse.com/i/vgGHo9)

=== "配置表单参数"

    [![vTz36J.png](https://s1.ax1x.com/2022/09/05/vTz36J.png)](https://imgse.com/i/vTz36J)

    !!! 提示
        如果user和group是多对一的关系，需填入**用户表Group外键字段** </br>
        如果user和group是多对多的关系，需填入**用户和组织多对多关系表**， **用户组织关系表User外键字段**， **用户组织关系表Group外键字段**</br>
        group上下级之间关联的字段需要设置**组织表Parent外键字段**</br>
        用户和组织属性映射列表中必须存在target_attr为id的映射, 此处id为SCIM协议中user和group的唯一标识


### 配置从源数据库同步数据到Client数据库

=== "打开**SCIM数据同步**页面, 点击创建"
    [![vgGHo9.png](https://s1.ax1x.com/2022/08/24/vgGHo9.png)](https://imgse.com/i/vgGHo9)


=== "配置SQL Server同步Client"

    [![vTzTns.png](https://s1.ax1x.com/2022/09/05/vTzTns.png)](https://imgse.com/i/vTzTns)

    !!! 提示
        如果user和group是多对一的关系，需填入**用户表Group外键字段** </br>
        如果user和group是多对多的关系，需填入**用户和组织多对多关系表**， **用户组织关系表User外键字段**， **用户组织关系表Group外键字段**</br>
        group上下级之间关联的字段需要设置**组织表Parent外键字段**</br>
        用户和组织属性映射列表中必须存在source_attr为id的映射，用于匹配Server和Client数据库中的数据, 判断数据是否已经同步过


### 查看Server数据库表数据

=== "查看源数据库groups"
    
    [![v7ST2D.png](https://s1.ax1x.com/2022/09/05/v7ST2D.png)](https://imgse.com/i/v7ST2D)

=== "查看源数据库users"
    
    [![v7SbKH.png](https://s1.ax1x.com/2022/09/05/v7SbKH.png)](https://imgse.com/i/v7SbKH)

=== "查看源数据库users_groups"
    
    [![v7SXVI.png](https://s1.ax1x.com/2022/09/05/v7SXVI.png)](https://imgse.com/i/v7SXVI)


### 查看Client数据库表数据

=== "查看Client数据库groups"
    
    [![v7Sqrd.png](https://s1.ax1x.com/2022/09/05/v7Sqrd.png)](https://imgse.com/i/v7Sqrd)

=== "查看Client数据库users"
    
    [![v7SLqA.png](https://s1.ax1x.com/2022/09/05/v7SLqA.png)](https://imgse.com/i/v7SLqA)

=== "查看Client数据库users_groups"
    
    [![v7S7xe.png](https://s1.ax1x.com/2022/09/05/v7S7xe.png)](https://imgse.com/i/v7S7xe)
