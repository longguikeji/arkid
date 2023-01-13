# LDAP SERVER

## 功能介绍

ldap协议插件，因协议特殊性需配合[arkid_ldap_server服务端 版本：2.5.x](https://github.com/longguikeji/arkid_ldap_server/tree/v2.5-dev)来实现协议功能

<b color="red">本插件仅以arkid数据为基础，实现LDAP协议的认证与搜索功能。</b>

## 配置指南

### arkid_ldap_server服务端部署
    
联系管理员或运维工作人员确认已完成[arkid_ldap_server服务端 版本：2.5.x](https://github.com/longguikeji/arkid_ldap_server/tree/v2.5-dev)的部署,或参考下列文档自行部署：
    
=== "k8s helm安装的arkid，添加ldap"
    + 创建ldap所需的yaml文件

    ```yaml
        ---
        apiVersion: v1
        kind: Service
        metadata:
        name: arkid-ldapjs
        spec:
        type: NodePort
        ports:
        - name: ldap
            nodePort: 32581
            port: 389
            protocol: TCP
            targetPort: 1389
        selector:
            app.kubernetes.io/instance: arkid
            app.kubernetes.io/name: arkid-ldapjs
        ---
        apiVersion: apps/v1
        kind: Deployment
        metadata:
        name: arkid-ldapjs
        spec:
        selector:
            matchLabels:
            app.kubernetes.io/instance: arkid
            app.kubernetes.io/name: arkid-ldapjs
        template:
            metadata:
            labels:
                app.kubernetes.io/instance: arkid
                app.kubernetes.io/name: arkid-ldapjs
            spec:
            containers:
            - env:
                - name: TZ
                value: Asia/Shanghai
                - name: BEURL
                value: http://dev-arkidv2-be
                image: registry.cn-zhangjiakou.aliyuncs.com/ark-releases/ldapjs:latest
                imagePullPolicy: IfNotPresent
                name: arkid-ldapjs
                resources: {}
            initContainers:
            - command:
                - sh
                - -c
                - sysctl -w net.core.somaxconn=65535
                image: busybox
                imagePullPolicy: Always
                name: setsysctl
                resources: {}
                securityContext:
                privileged: true
    ```

    可能需要修改的地方

    ``` yaml
        args:
            - "http://arkid-be"
        // 这个位置需要填arkid后端的service名字
    ```

    + k8s 安装ldap，安装在arkid 所在的命名空间中

    ``` bash
        kubectl -n arkid apply -f ldap.yaml
    ```

=== "docker-compose安装的arkid，添加ldap部署"
    + 修改docker-compose.yml 文件，将注释掉的ldap部分解除注释
    + 然后再执行命令

    ``` bash
        docker-compose up -d
    ```

=== "在arkid平台上启用LDAPSERVER"
    + 租赁插件： 租户管理员从左侧菜单栏依次进入【租户管理】->【插件管理】,在插件租赁页面中选择租赁LDAP server插件:
        [![租赁插件](https://s1.ax1x.com/2022/08/01/vkTNqJ.png)](https://imgtu.com/i/vkTNqJ)
    + 租赁成功后，在已租赁插件列表中找到LDAP server插件,点击【租户配置】按钮,配置相关信息：
        [![配置插件](https://s1.ax1x.com/2022/08/01/vk7jne.md.png)](https://imgtu.com/i/vk7jne)
        - 注意用户/群组信息字段映射一栏中映射名为LDAP协议中用户/群组的属性名，字段名为arkid平台中的用户/群组属性字段名，如不填则会使用默认配置
    + 配置完成后进入【身份数据源】【LDAP SERVER】一栏中，此处会显示相关客户端所需信息：
        [![身份数据源](https://s1.ax1x.com/2022/08/01/vkHyHH.md.png)](https://imgtu.com/i/vkHyHH)

=== "在LDAP Admin中链接ARKID LDAP SERVER"
    + 创建链接:<br/>
        [![创建链接](https://s1.ax1x.com/2022/08/01/vkHbUs.md.png)](https://imgtu.com/i/vkHbUs)
        - 登录名即为上一步骤中身份数据源显示的登录名
        - 密码为arkid用户密码
    + 用户搜索:<br/>
        [![用户搜索](https://s1.ax1x.com/2022/08/01/vkbmrD.md.png)](https://imgtu.com/i/vkbmrD)
    + 群组搜索:<br/>
        [![群组搜索](https://s1.ax1x.com/2022/08/01/vkb6MT.md.png)](https://imgtu.com/i/vkb6MT)
        - 注意：群组CN映射为arkid群组模型的id而非name