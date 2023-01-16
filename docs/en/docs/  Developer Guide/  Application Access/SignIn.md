# sign in

Although ARKID can support various application access protocols through plugins，But we recommend using OIDC to complete access。

For different application protocols，Please refer to the documents of their respective plugins：

* [OAuth2](../../../%20%20System plug -in/com_Dragon turtle_app_protocol_oidc/Oueth2/)
* [OIDC](../../../%20%20System plug -in/com_Dragon turtle_app_protocol_oidc/OIDC/)
* [SAML2](../../../%20Other plug -in/com_Dragon turtle_app_protocol_saml2/)
* [CAS](../../../%20Other plug -in/com_Dragon turtle_app_protocol_cas_server/)

etc.，Other protocols can find the corresponding plug -in support in the plug -in store

If you encounter an agreement that has not yet supported，Welcome to leave a message in gitee or github to us

## ArkStoreApplication access

If you are a developer of SaaS app，Then you need to complete the application access and submit it to ArkStore in the center ARKID。

ArkStoreApplication access，We support the following methods：

* OIDCprotocol
* Dense replacement
* sponsored links
* customize

### OIDCprotocol
1.In [Central Arkid] (https://central.arkid.cc/)，Click on application management-Application List-create，Create an application

[![v6uRe0.md.jpg](https://s1.ax1x.com/2022/08/22/v6uRe0.md.jpg)](https://imgse.com/i/v6uRe0)

2.Click the protocol configuration of the center ARKID application，App Type selection OIDC-Platform，Configure the content of the corresponding content of the OIDC protocol

[![v6Kulj.md.jpg](https://s1.ax1x.com/2022/08/22/v6Kulj.md.jpg)](https://imgse.com/i/v6Kulj)

3.In [ArkStore] (https://sheet.longguikeji.com/)，Click on developer-Application management-Add application，Add application

[![v6uxYD.md.jpg](https://s1.ax1x.com/2022/08/22/v6uxYD.md.jpg)](https://imgse.com/i/v6uxYD)

``` title="Replenishment"
The access method selects OIDC
Application ID fields created by the application ID field，You can edit the application in the center Arkid to view
```

4.After adding an application in ArkStore，Click to submit review，Long Gui will review your application，After passing, the market will be set to ArkStore Application Market

### Dense replacement
Not from Arkid V2 migrate to V2.5

### sponsored links
1.In [Central Arkid] (https://central.arkid.cc/)，Click on application management-Application List-create，Create an application

[![v6uRe0.md.jpg](https://s1.ax1x.com/2022/08/22/v6uRe0.md.jpg)](https://imgse.com/i/v6uRe0)

2.In [ArkStore] (https://sheet.longguikeji.com/)，Click on developer-Application management-Add application，Add application

[![v6uxYD.md.jpg](https://s1.ax1x.com/2022/08/22/v6uxYD.md.jpg)](https://imgse.com/i/v6uxYD)

``` title="Replenishment"
The access method selects the promotion link
Application ID fields created by the application ID field，You can edit the application in the center Arkid to view
```

3.After adding an application in ArkStore，Click to submit review，Long Gui will review your application，After passing, the market will be set to ArkStore Application Market

### customize

If your application does not want to access any of the following ways，If you want to access it with a self -defined protocol，Welcome to contact us： support@longguikeji.com
