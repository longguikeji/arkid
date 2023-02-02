# FeiShu User data synchronous plugin

## Features
1. ServerThe model implements users and organizations that can obtain corporate WeChat through standard SCIM interfaces
2. ClientThe mode is implemented. Users and organizations in Server, Synchronous to corporate WeChat

## WeChatWork Server

### Create a wechatwork application

=== "Open the corporate WeChat management background，Create an application"
    [![vSeLYF.png](https://s1.ax1x.com/2022/07/26/vSeLYF.png)](https://imgtu.com/i/vSeLYF)

=== "Fill in the form"
    [![vSmESH.png](https://s1.ax1x.com/2022/07/26/vSmESH.png)](https://imgtu.com/i/vSmESH)

=== "Save secret (corresponding parameter Corpsecret)"
    [![vSmGlj.png](https://s1.ax1x.com/2022/07/26/vSmGlj.png)](https://imgtu.com/i/vSmGlj)

=== "Save the enterprise ID (corresponding parameter Corpid)"
    [![vSmXAf.png](https://s1.ax1x.com/2022/07/26/vSmXAf.png)](https://imgtu.com/i/vSmXAf)

### Update corporate WeChat trusted domain name

=== "Log in Enterprise Management Backstage->Self -building application that needs to be opened->Clicked Web authority and js-SDK"
    [![vELBKP.md.jpg](https://s1.ax1x.com/2022/08/02/vELBKP.md.jpg)](https://imgtu.com/i/vELBKP)

=== "Set the trusted domain name"
    [![vEL6Ug.md.jpg](https://s1.ax1x.com/2022/08/02/vEL6Ug.md.jpg)](https://imgtu.com/i/vEL6Ug)

=== "Click the credible IP"
    [![vEOVMt.md.jpg](https://s1.ax1x.com/2022/08/02/vEOVMt.md.jpg)](https://imgtu.com/i/vEOVMt)

=== "Configuration IP"
    [![vEOYLV.md.jpg](https://s1.ax1x.com/2022/08/02/vEOYLV.md.jpg)](https://imgtu.com/i/vEOYLV)

=== "The server IP can be obtained by using the terminal ping website"
    [![vEORoD.md.jpg](https://s1.ax1x.com/2022/08/02/vEORoD.md.jpg)](https://imgtu.com/i/vEORoD)

### Open the company's WeChat address book synchronization function

=== "Log in Enterprise Management Backstage->Enter the management tool->Clicked Synchronous address book synchronization"
    [![BdYYZU.jpg](https://v1.ax1x.com/2023/01/17/BdYYZU.jpg)](https://zimgs.com/i/BdYYZU)

=== "Configuration IP"
    [![BdYXAI.jpg](https://v1.ax1x.com/2023/01/17/BdYXAI.jpg)](https://zimgs.com/i/BdYXAI)

=== "The server IP can be obtained by using the terminal ping website"
    [![vEORoD.md.jpg](https://s1.ax1x.com/2022/08/02/vEORoD.md.jpg)](https://imgtu.com/i/vEORoD)

=== "Save secret (corresponding parameter Syncsecret)"
    [![vSmXAf.png](https://s1.ax1x.com/2022/07/26/vSmXAf.png)](https://imgtu.com/i/vSmXAf)

### Configure the company's WeChat service terminal

=== "Click the identity data source>SCIM data synchronization>Click to create"
    [![BdYidB.jpg](https://v1.ax1x.com/2023/01/17/BdYidB.jpg)](https://zimgs.com/i/BdYidB)

=== "View the generated users and groups"
    [![BdYeVw.jpg](https://v1.ax1x.com/2023/01/17/BdYeVw.jpg)](https://zimgs.com/i/BdYeVw)

## WeChatWork Client

### The client configured weChatwork

=== "Click the identity data source>SCIM data synchronization>Click to create"
    [![BdrTYf.jpg](https://v1.ax1x.com/2023/01/17/BdrTYf.jpg)](https://zimgs.com/i/BdrTYf)
