# Novice tutorial

The following introduces the growth path of a novice administrator

!!! Preparation

    Create tenants in the SaaS system，Or after the privatization deployment is deployed, log in with the Admin account，You can continue the following operations
## Add the first OIDC application

=== "Open the application list"

    [![X40bd0.jpg](https://s1.ax1x.com/2022/06/14/X40bd0.jpg)](https://imgtu.com/i/X40bd0)

=== "Click to create，Fill in the form"

    After clicking to confirm，Dialog box closed，You can see the application you created。

    [![XhxYWV.jpg](https://s1.ax1x.com/2022/06/14/XhxYWV.jpg)](https://imgtu.com/i/XhxYWV)

=== "Click the protocol configuration"

    [![XhxBw9.jpg](https://s1.ax1x.com/2022/06/14/XhxBw9.jpg)](https://imgtu.com/i/XhxBw9)

=== "Fill in configuration"
    Application type selection as OIDC，Fill in the parameter，Complete

    [![XhxyJx.jpg](https://s1.ax1x.com/2022/06/14/XhxyJx.jpg)](https://imgtu.com/i/XhxyJx)

=== "Click the protocol configuration again"
    You can view all related parameters of the protocol。
    
    The meaning of related parameters，Please refer to the [OIDC plug -in document] (../../%20%20 system plug -in/com_Dragon turtle_app_protocol_oidc/OIDC/)

    [![Xhx5TA.jpg](https://s1.ax1x.com/2022/06/14/Xhx5TA.jpg)](https://imgtu.com/i/Xhx5TA)



## Add a new account
=== "Open the user list"

    [![X4BBkV.jpg](https://s1.ax1x.com/2022/06/14/X4BBkV.jpg)](https://imgtu.com/i/X4BBkV)

=== "Click to create"
    Fill in the form below，Just click to create。

    [![X4BrfU.jpg](https://s1.ax1x.com/2022/06/14/X4BrfU.jpg)](https://imgtu.com/i/X4BrfU)




## Add an organizational structure or role

=== "Open the user group"
    You can see about the detailed introduction to the grouping [User Management-User grouping] (../User Manual/%20Tenants Administrator/User Management/#_3)

    [![X4TpdK.jpg](https://s1.ax1x.com/2022/06/14/X4TpdK.jpg)](https://imgtu.com/i/X4TpdK)

=== "Click to create"
    Fill in the form below，Just click to create。

    [![X4Tndf.jpg](https://s1.ax1x.com/2022/06/14/X4Tndf.jpg)](https://imgtu.com/i/X4Tndf)

=== "Add users to group"

    [![X4TGyn.jpg](https://s1.ax1x.com/2022/06/14/X4TGyn.jpg)](https://imgtu.com/i/X4TGyn)

=== "Choose a user"

    [![X4T0W4.jpg](https://s1.ax1x.com/2022/06/14/X4T0W4.jpg)](https://imgtu.com/i/X4T0W4)

## Open an application for the target account


## Open a set of permissions for the target organizational structure
## Add mobile verification code as a new authentication factor

=== "Open the authentication factor"

    [![X4Tndf.jpg](https://s1.ax1x.com/2022/06/14/X4Tndf.jpg)](https://imgtu.com/i/X4Tndf)

=== "Click to create"

    Choose the type of authentication factors“mobile”，Fill in the form


=== "Open the authentication factor"


## ADSynchronize with Arkid's data

Configure users and organizations in synchronous AD to ARKID

=== "Open SCIM data synchronization，Click to create"

    [![vgGHo9.png](https://s1.ax1x.com/2022/08/24/vgGHo9.png)](https://imgse.com/i/vgGHo9)

=== "Configure AD synchronization server"

    [![vgYMnO.png](https://s1.ax1x.com/2022/08/24/vgYMnO.png)](https://imgse.com/i/vgYMnO)

=== "Configure Arkid synchronization client"

    !!! hint
        SCIMSynchronous server: Choose the previous step created Ad synchronous server</br>
        Timing time: Format refer to linux crontab, The figure below indicates every day 11：51 Run timing synchronization task
        The timing task needs to start Clery work and beat:</br>
        celery -A arkid.core.tasks.celery beat -l debug</br>
        celery -A arkid.core.tasks.celery worker -l debug

    [![vgY3AH.png](https://s1.ax1x.com/2022/08/24/vgY3AH.png)](https://imgse.com/i/vgY3AH)

=== "View source data in AD"
    
    [![vgYfDU.png](https://s1.ax1x.com/2022/08/24/vgYfDU.png)](https://imgse.com/i/vgYfDU)

=== "View data in Arkid"
    
    [![vgYIUJ.png](https://s1.ax1x.com/2022/08/24/vgYIUJ.png)](https://imgse.com/i/vgYIUJ)

## Enable multiple tenants，Become IDAAS
