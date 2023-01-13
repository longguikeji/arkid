# 数据库用户和组织数据同步插件

## 功能介绍
1. Server模式实现了可以通过标准SCIM接口获取数据库服务器中的用户和组织
2. Client模式实现了可以通过定时任务拉取SCIM Server中的用户和组织, 同步到客户端数据库中
3. 此插件暂时只支持mysql和sqlserver

## 配置两个Mysql数据库之间数据库同步

### 创建两个数据库和表

- 创建作为提供同步数据的Server数据库，建立**sync_users**, **sync_groups**表， 以及user所属groups的中间表**sync_users_groups_rel**, </br>
**sync_users_groups_rel**中间表中user_id外键关联sync_users(id)， group_id外键关联sync_groups(id)
    
    !!! 提示
        此例中演示user和group之间是ManyToMany的关系, 如果user只属于一个group，可以在**sync_users**表中定义group_id，外键关联sync_groups(id)

- 创建Client数据库，用于将Server数据库提供的数据同步到Client数据库

    !!! 注意
        为演示方便，Client数据库中的表定义和Server数据库一样,实际生产环境中可能不同

### 配置 Mysql 源数据库

=== "打开**SCIM数据同步**页面，点击创建"
    [![BjpL33.png](https://v1.ax1x.com/2023/01/03/BjpL33.png)](https://zimgs.com/i/BjpL33)

=== "配置表单参数"

    [![Bjp05j.png](https://v1.ax1x.com/2023/01/03/Bjp05j.png)](https://zimgs.com/i/Bjp05j)

    !!! 提示
        如果user和group是多对一的关系，需填入**用户表Group外键字段** </br>
        如果user和group是多对多的关系，需填入**用户和组织多对多关系表**， **用户组织关系表User外键字段**， **用户组织关系表Group外键字段**</br>
        group上下级之间关联的字段需要设置**组织表Parent外键字段**</br>
        用户和组织属性映射列表中必须存在target_attr为id的映射, 此处id为SCIM协议中user和group的唯一标识

=== "配置用户属性映射"

    [![Bjp3C5.png](https://v1.ax1x.com/2023/01/03/Bjp3C5.png)](https://zimgs.com/i/Bjp3C5)

=== "配置组织属性映射"

    [![Bjp7Bm.png](https://v1.ax1x.com/2023/01/03/Bjp7Bm.png)](https://zimgs.com/i/Bjp7Bm)

### 配置从源数据库同步数据到Client数据库

=== "打开**SCIM数据同步**页面, 点击创建"

    [![BjpL33.png](https://v1.ax1x.com/2023/01/03/BjpL33.png)](https://zimgs.com/i/BjpL33)


=== "配置 Mysql 同步Client"

    [![BjpEb4.png](https://v1.ax1x.com/2023/01/03/BjpEb4.png)](https://zimgs.com/i/BjpEb4)

    !!! 提示
        如果user和group是多对一的关系，需填入**用户表Group外键字段** </br>
        如果user和group是多对多的关系，需填入**用户和组织多对多关系表**， **用户组织关系表User外键字段**， **用户组织关系表Group外键字段**</br>
        group上下级之间关联的字段需要设置**组织表Parent外键字段**</br>
        用户和组织属性映射列表中必须存在source_attr为id的映射，用于匹配Server和Client数据库中的数据, 判断数据是否已经同步过


### 查看Server数据库表数据

=== "查看源数据库groups"
    
    [![BjpQRh.png](https://v1.ax1x.com/2023/01/03/BjpQRh.png)](https://zimgs.com/i/BjpQRh)

=== "查看源数据库users"
    
    [![BjpNZ9.png](https://v1.ax1x.com/2023/01/03/BjpNZ9.png)](https://zimgs.com/i/BjpNZ9)

=== "查看源数据库users和groups关系数据"
    
    [![BjpuqY.png](https://v1.ax1x.com/2023/01/03/BjpuqY.png)](https://zimgs.com/i/BjpuqY)


### 查看Client数据库表数据

=== "查看Client数据库groups"
    
    [![BjpwDH.png](https://v1.ax1x.com/2023/01/03/BjpwDH.png)](https://zimgs.com/i/BjpwDH)

=== "查看Client数据库users"
    
    [![BjpyMZ.png](https://v1.ax1x.com/2023/01/03/BjpyMZ.png)](https://zimgs.com/i/BjpyMZ)

=== "查看Client数据库users和groups关系数据"
    
    [![BjpK3U.png](https://v1.ax1x.com/2023/01/03/BjpK3U.png)](https://zimgs.com/i/BjpK3U)
