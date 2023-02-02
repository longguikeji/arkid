# DingDing User data synchronous plugin

## Features
1. ServerThe mode implements users and organizations that can obtain dingding through standard SCIM interfaces
2. ClientThe mode is implemented. Users and organizations in Server, Sync to dingding

## DingDing Server

### First become a nail developer
    For details, please refer to [becoming a nail developer] (https://open.dingtalk.com/document/org/become-a-dingtalk-developer)
    Please refer to the link to the configuration nail application [Realize the third -party website] (HTTPS://open.dingtalk.com/document/orgapp-server/tutorial-obtaining-user-personal-information)

### Login nail developer background，Create and configure the application

=== "Click to create an application"
    [![jzIFGn.png](https://s1.ax1x.com/2022/07/26/jzIFGn.png)](https://imgtu.com/i/jzIFGn)

=== "Fill in the form parameter"
    [![jzIaIH.png](https://s1.ax1x.com/2022/07/26/jzIaIH.png)](https://imgtu.com/i/jzIaIH)

=== "Save the app Key and app Secret"
    [![jzoSQx.png](https://s1.ax1x.com/2022/07/26/jzoSQx.png)](https://imgtu.com/i/jzoSQx)

=== "Configure development management information"
    [![jzo07F.png](https://s1.ax1x.com/2022/07/26/jzo07F.png)](https://imgtu.com/i/jzo07F)

=== "Add personal rights"
    [![Bj0RaQ.jpg](https://v1.ax1x.com/2023/01/04/Bj0RaQ.jpg)](https://zimgs.com/i/Bj0RaQ)

=== "Add communication records (1)"
    [![Bj0YIf.jpg](https://v1.ax1x.com/2023/01/04/Bj0YIf.jpg)](https://zimgs.com/i/Bj0YIf)

=== "Add communication records (2)"
    [![Bj0t0c.jpg](https://v1.ax1x.com/2023/01/04/Bj0t0c.jpg)](https://zimgs.com/i/Bj0t0c)

=== "Add obtaining vouchers permissions"
    [![Bj0z53.jpg](https://v1.ax1x.com/2023/01/04/Bj0z53.jpg)](https://zimgs.com/i/Bj0z53)

### Configure the dingding server

=== "Click the identity data source>SCIM data synchronization>Click to create"
    [![Bj044j.jpg](https://v1.ax1x.com/2023/01/04/Bj044j.jpg)](https://zimgs.com/i/Bj044j)

=== "View the generated users and groups"
    [![BiGa7V.jpg](https://v1.ax1x.com/2023/01/12/BiGa7V.jpg)](https://zimgs.com/i/BiGa7V)

## DingDing Client

### Configure dingding client

=== "Click the identity data source>SCIM data synchronization>Click to create"

    Here is the AppKey and AppSecret of Dingding，Introducing the user's mobile phone number requires the only one in the enterprise，All users must have a department，Users without a department cannot synchronize

    [![Bj0Xbm.jpg](https://v1.ax1x.com/2023/01/04/Bj0Xbm.jpg)](https://zimgs.com/i/Bj0Xbm)
