# Alibaba Cloud Configuration

## Alibaba Cloud User SSO

=== "Create an application"
    Log in to the ARKID platform，Enter【Application management】-> 【Application List】, Clicked【Add to】Button, Create an application called Alibaba Cloud User SSO，URL does not fill in the URL<br/>
    [![XqCHYV.md.png](https://s1.ax1x.com/2022/06/17/XqCHYV.md.png)](https://imgtu.com/i/XqCHYV)

=== "Download SP metadata file"
    Log in to Alibaba Cloud Platform，Enter the access control page through the avatar drop -down menu，Select the user SSO in the SSO management column，copy【SAML Service provider metadata data URL】And download the file<br/>
    [![XqCIwn.md.png](https://s1.ax1x.com/2022/06/17/XqCIwn.md.png)](https://imgtu.com/i/XqCIwn)

=== "Configuration protocol"
    Click on the right side in Arkid【Configuration protocol】The button enters the protocol configuration window，Select the protocol type `<b>`Gathering_Aliyunram `</b>`，Fill in related data in turn<br/>
    + sp metadataThe file is the data file downloaded in the previous step<br/>
    + See Alibaba Cloud [Document] (https] (https] (HTTPS://help.alien.com/document_detail/144277.html)<br/>
    [![XqC7F0.md.png](https://s1.ax1x.com/2022/06/17/XqC7F0.md.png)](https://imgtu.com/i/XqC7F0)

=== "Download IDP metadata file"
    Click again after confirmation【Configuration protocol】Button,Copy IDP entity ID of ID, download IDP metad data file spare<br/>
    [![XqCbWT.md.png](https://s1.ax1x.com/2022/06/17/XqCbWT.md.png)](https://imgtu.com/i/XqCbWT)

=== "Upload IDP metad data file"
    Back to the Alibaba Cloud Platform page again，Click Edit User SSO Upload the IDP metad data file just downloaded<br/>
    [![XqCLSU.md.png](https://s1.ax1x.com/2022/06/17/XqCLSU.md.png)](https://imgtu.com/i/XqCLSU)

=== "Log in to Alibaba"
    Click to confirm，Back to the Arkid Unified Certification Platform Desktop，At this time, click on Alibaba Cloud User SSO Application Card，After a few jumps, you can enter the Alibaba Cloud Platform<br/>
    [![XqCxm9.md.png](https://s1.ax1x.com/2022/06/17/XqCxm9.md.png)](https://imgtu.com/i/XqCxm9)

=== "Notice"
    + About the domain name：Alibaba Cloud provides auxiliary domain name/Domain name/Set SSO domain name in the default domain name，Use auxiliary domain name in the example，Please refer to the configuration of other domain names on Alibaba Cloud<br/>
    + User SSO needs to be added to Alibaba Cloud in advance，And keep it consistent with the user name on the ARKID platform，For example, Arkid user admin Corresponding to the Alibaba Cloud Platform users are admin@arkid<br/>
    [![XqCXy4.md.png](https://s1.ax1x.com/2022/06/17/XqCXy4.md.png)](https://imgtu.com/i/XqCXy4)

## Alibaba Cloud Character SSO

=== "Preparation"
    + Download [Alibaba Cloud SP metadata file] (HTTPS://sign in.alien.com/saml-role/sp-Meta.xml)

=== "Create an application"
    Log in to the ARKID platform，Enter【Application management】-> 【Application List】, Clicked【Add to】Button, Create an application called Alibaba Cloud character SSO，URL does not fill in the URL<br/>
    [![Xq9456.md.png](https://s1.ax1x.com/2022/06/17/Xq9456.md.png)](https://imgtu.com/i/Xq9456)

=== "Configuration protocol"
    After the addition is completed, click on the right on the right【Configuration protocol】The button enters the protocol configuration window，Select the protocol type <b>Gathering_He'll fight </b>，Fill in related data in turn<br/>
        + sp metadataThe file is the data file downloaded at the preparation work<br/>
        + RoleThere is no corresponding data at present，Can be placed as empty，The author is used here"arkid"Occupy<br/>
    [![Xq9IPK.md.png](https://s1.ax1x.com/2022/06/17/Xq9IPK.md.png)](https://imgtu.com/i/Xq9IPK)

=== "Download IDP metadata file"
    Click to confirm after the configuration is completed，Click again in the list【Configuration protocol】The button enters the configuration protocol popup window，Copy IDP entity ID of ID, download IDP metad data file spare<br/>
    [![Xq9o8O.md.png](https://s1.ax1x.com/2022/06/17/Xq9o8O.md.png)](https://imgtu.com/i/Xq9o8O)

=== "Create identity provider"
    Log in to Alibaba Cloud Platform，Enter the menu menu of the avatar in the upper right corner【Access control】page，At【SSO management】Page select SAML protocol->Character SSO->Create identity provider，Upload the metadata file downloaded in one step here，After the creation is completed, click the identity provider just created，Find the identity provider ARN for later on the detailed page<br/>
    [![Xq9hUx.md.png](https://s1.ax1x.com/2022/06/17/Xq9hUx.md.png)](https://imgtu.com/i/Xq9hUx)<br/>
    [![Xq9T2D.md.png](https://s1.ax1x.com/2022/06/17/Xq9T2D.md.png)](https://imgtu.com/i/Xq9T2D)

=== "Creating a Role"
    Identification->In the character column，Creating a Role，Type selection identity provider,Click Next<br/>
    [![Xq9bKH.md.png](https://s1.ax1x.com/2022/06/17/Xq9bKH.md.png)](https://imgtu.com/i/Xq9bKH)

=== "Configuration role"
    When configured the role，Identity provider type selection SAML，Identity provider chooses the identity provider created earlier，Click to complete<br/>
    [![Xq97xe.md.png](https://s1.ax1x.com/2022/06/17/Xq97xe.md.png)](https://imgtu.com/i/Xq97xe)

=== "Role authorization"
    After the character is created, the character must be authorized，I won't go into details here

=== "Character ARN"
    After the above steps are completed，Click the character just created，Copy the character ARN spare<br/>
    [![Xq9qrd.md.png](https://s1.ax1x.com/2022/06/17/Xq9qrd.md.png)](https://imgtu.com/i/Xq9qrd)

=== "Modify protocol configuration"
    Back to the ARKID certification platform，Fill in the value of the ROLE column in the protocol configuration pop -up box，Format 【Character ARN】,【Identity provider ARN】,Pay attention to the half -angle between the two ARN（English sentence）Commas。<br/>
    [![Xq9o8O.md.png](https://s1.ax1x.com/2022/06/17/Xq9o8O.md.png)](https://imgtu.com/i/Xq9o8O)
  
=== "Log in to Alibaba"
    Return to the Arkid certification platform desktop，Click on Alibaba Cloud Character SSO Application Card，After multiple jumps, you can correspond to the role to enter the Alibaba Cloud platform<br/>
    [![Xq9XVI.md.png](https://s1.ax1x.com/2022/06/17/Xq9XVI.md.png)](https://imgtu.com/i/Xq9XVI)

