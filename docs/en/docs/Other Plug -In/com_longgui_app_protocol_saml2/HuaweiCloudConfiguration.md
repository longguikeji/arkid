# Huawei Cloud Configuration

## Huawei Cloud Virtual User SSO

=== "Preparation"
    Download Huawei Yungong Public Platform Metadata File：https://auth.huawei cloud.com/Othui/saml/Meta.xml

=== "Create identity provider"
    Log in to Huawei Yungong Public Platform，Enter【Console】，Find unified identity certification service，Create identity provider<br/>
    [![Xq9k4K.md.png](https://s1.ax1x.com/2022/06/17/Xq9k4K.md.png)](https://imgtu.com/i/Xq9k4K)

=== "Copy the login link"
    After the creation is completed, enter the modified identity provider page，Copy the login link to the clipboard for later use<br/>
    [![Xq9E9O.md.png](https://s1.ax1x.com/2022/06/17/Xq9E9O.md.png)](https://imgtu.com/i/Xq9E9O)

=== "Create an application"
    Log in to the ARKID platform，Enter【Application management】-> 【Application List】, Clicked【Add to】Button, Create an application called Huawei Cloud Virtual User SSO，Application URL is filled in a copy of the copy<br/>
    [![Xq9FN6.md.png](https://s1.ax1x.com/2022/06/17/Xq9FN6.md.png)](https://imgtu.com/i/Xq9FN6)

=== "Configuration protocol"
    Click on the right side in Arkid【Configuration protocol】The button enters the protocol configuration window，Select the protocol type `<b>`Gathering_Meta `</b>`，Fill in related data in turn：<br/>
    sp metadataThe file is the data file downloaded earlier<br/>
    [![Xq9iAx.md.png](https://s1.ax1x.com/2022/06/17/Xq9iAx.md.png)](https://imgtu.com/i/Xq9iAx)

=== "Get IDP metad data file"
    Click again after confirmation【Configuration protocol】Button,Copy IDP entity ID of ID, download IDP metad data file spare<br/>
    [![Xq9CH1.md.png](https://s1.ax1x.com/2022/06/17/Xq9CH1.md.png)](https://imgtu.com/i/Xq9CH1)

=== "Modify identity provider"
    Return to Huawei Yungong Public Platform，Upload the IDP just downloaded in the modified identity provider page Metadata file<br/>
    [![Xq9V3D.md.png](https://s1.ax1x.com/2022/06/17/Xq9V3D.md.png)](https://imgtu.com/i/Xq9V3D)

=== "Jump login"
    Enter Arkid Desktop,Click Huawei Cloud Application，After several page jumps，Successful entering Huawei Cloud Platform,Show login user as feederationUser<br/>
    [![Xq9ejH.md.png](https://s1.ax1x.com/2022/06/17/Xq9ejH.md.png)](https://imgtu.com/i/Xq9ejH)
