# LDAP SERVER

## Features

ldapProtocol plugin，Due to the particularity of the agreement, it needs to be matched with [ARKID_ldap_Server service Version：2.5.x](https://github.com/Dragon Turtle Technology/arkid_ldap_server/tree/Category.5-DEV) to implement the protocol function

<b color="red">This plug -in is based on Arkid data，Implement the LDAP protocol certification and search function。</b>

## Configuration guide

### arkid_ldap_serverServer deployment
    
Contact the administrator or operation and maintenance staff to confirm that the [ARKID_ldap_Server service Version：2.5.x](https://github.com/Dragon Turtle Technology/arkid_ldap_server/tree/Category.5-DEV) deployment,Or refer to the following documents to deploy yourself by yourself：
    
=== "k8s helmThe installed Arkid，Add LDAP"
    + Create the yaml file required for LDAP

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

    Place that may need to be modified

    ``` yaml
        args:
            - "http://arkid-be"
        // This location needs to be filled in the service name of the ARKID back end
    ```

    + k8s Install LDAP，Installed in Arkid In the name space where you live

    ``` bash
        kubectl -n arkid apply -f ldap.yaml
    ```

=== "docker-composeThe installed Arkid，Add LDAP deployment"
    + Modify docker-compose.yml document，Remove the comments from the comments
    + Then execute the command

    ``` bash
        docker-compose up -d
    ```

=== "LDAPSERVER on the Arkid platform"
    + Lease plug -in： Practitioner administrator enters from the menu bar on the left【Tenant management】->【Plug -in management】,Select the lease LDAP in the plug -in lease page Server plugin:
        [![Lease plugin] (https://S1.ax1x.com/2022/08/01/vktnqj.png)](https://imgtu.com/i/vktnqj)
    + After the lease is successful，Find LDAP in the list of leased plugins Server plugin,Clicked【Tenant configuration】Button,Configure related information：
        [![Configure plug -in] (https://S1.ax1x.com/2022/08/01/vk7jne.md.png)](https://imgtu.com/i/vk7jne)
        - Pay attention to users/Group information field mapping column is mapped in the LDAP protocol, users in the LDAP protocol/The attribute name of the group，The field is called the user in the ARKID platform/Group attribute field name，If you do not fill it, you will use the default configuration
    + Enter after the configuration is completed【Identity data source】【LDAP SERVER】In the column，The information required by the relevant client will be displayed here：
        [![Identity data source] (https://S1.ax1x.com/2022/08/01/VKHYHH.md.png)](https://imgtu.com/i/VKHYHH)

=== "In LDAP Link arkid in admin LDAP SERVER"
    + Create a link:<br/>
        [![Create link] (https://S1.ax1x.com/2022/08/01/vkHbUs.md.png)](https://imgtu.com/i/vkHbUs)
        - Login name is the login name displayed in the identity data source in the previous step
        - The password is ARKID user password
    + User search:<br/>
        [![User search] (https://S1.ax1x.com/2022/08/01/VKBMrd.md.png)](https://imgtu.com/i/VKBMRD)
    + Group search:<br/>
        [![Group search] (https://S1.ax1x.com/2022/08/01/vkb6MT.md.png)](https://imgtu.com/i/vkb6MT)
        - Notice：Group CN mapping is the ID of the ARKID group model instead of name
