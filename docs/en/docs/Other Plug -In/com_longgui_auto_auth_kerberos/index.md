# KerberosAutomatic login plug -in

## Features
Via this plug -in，You can automatically log in to Arkid with an account in AD domain, The premise that the company has configured the AD domain environment，Employee computers are also under domain management
Details on how to configure AD domain，See [AD domain configuration KERBEROS certification document] (HTTPS://www.Lack.com/Dragon Turtle Technology/Run/L 1 places)

### ADCreate an ARKID service account in the domain

=== "ADCreate an ARKID service account"
    [![vCtbjI.png](https://s1.ax1x.com/2022/07/28/vCtbjI.png)](https://imgtu.com/i/vCtbjI)

=== "Configure service account attribute"
    [![vCtz4g.png](https://s1.ax1x.com/2022/07/28/vCtz4g.png)](https://imgtu.com/i/vCtz4g)

### Export the keytab file corresponding to the Arkid service in AD 

=== "ADLine Windows Execute commands on the server"
    [![vCNZUU.png](https://s1.ax1x.com/2022/07/28/vCNZUU.png)](https://imgtu.com/i/vCNZUU)


### Configure Arkid Server

=== "ServerInstall the Kerberos client"

    centosExecute commands:  yum install Close-workstation Close-libs Close-devel

    !!! attention "Notice"
        The client software installed in other linux distributions may be different

=== "Modify the Kerberos client configuration file"

    [![vCdFKA.png](https://s1.ax1x.com/2022/07/28/vCdFKA.png)](https://imgtu.com/i/vCdFKA)
    

=== "ADThe exported KRB5.Keytab to put it/In ETC directory"

    [![vCdhMd.png](https://s1.ax1x.com/2022/07/28/vCdhMd.png)](https://imgtu.com/i/vCdhMd)

### Configure Arkid Kerberos plug -in

=== "Create an automatic login plug -in configuration"

    [![vCdbi8.png](https://s1.ax1x.com/2022/07/28/vCdbi8.png)](https://imgtu.com/i/vCdbi8)
    
### Configure browser

=== "Open the browser local site"

    [![vCwiJU.png](https://s1.ax1x.com/2022/07/28/vCwiJU.png)](https://imgtu.com/i/vCwiJU)

=== "Open advanced settings"

    [![vCwUTP.png](https://s1.ax1x.com/2022/07/28/vCwUTP.png)](https://imgtu.com/i/vCwUTP)
    
=== "Add Arkid site"

    [![vCwwY8.png](https://s1.ax1x.com/2022/07/28/vCwwY8.png)](https://imgtu.com/i/vCwwY8)

!!! attention "Notice"
    edgeCommon this settings with Chrome, Firefox needs another configuration method, </br>
    In addition, you can also set up a computer in the domain through the AD sendsing group strategy
    reference：[Through the group strategy, IE will automatically log in to the SP site with the current domain account number] ("https://www.cnblogs.com/love007/p/4082875.html")

### Test automatic login effect
    Browser open the Arkid address，No need to enter a password，Log in to Arkid with the current PC domain account
