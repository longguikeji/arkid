# AD User data synchronous plugin

## Features
1. ServerThe mode implements the user and organization in AD or OpenLDAP through the standard SCIM interface
2. ClientThe mode implements the user and organization in AD or OpenLDAP through the timing task
3. The following is based on OpenLDAP to explain how to configure the data between Arkid


### Configure OpenLDAP synchronous data to ARKID

=== "Installation plug -in"

    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the AD user data synchronization card in the plug -in rental page，Click to rent<br/>

    [![BO1nRB.png](https://v1.ax1x.com/2022/12/14/BO1nRB.png)](https://zimgs.com/i/BO1nRB)

=== "Configure OpenLDAP as a data source server"
    [![BO1IFt.png](https://v1.ax1x.com/2022/12/14/BO1IFt.png)](https://zimgs.com/i/BO1IFt)

=== "Configure Arkid as a data synchronization client"
    [![BO1fqb.png](https://v1.ax1x.com/2022/12/14/BO1fqb.png)](https://zimgs.com/i/BO1fqb)

=== "View the source data in OpenLDAP"
    
    [![BO1iae.png](https://v1.ax1x.com/2022/12/14/BO1iae.png)](https://zimgs.com/i/BO1iae)

=== "Verification data has been synchronized to Arkid"

    [![BO1sMP.png](https://v1.ax1x.com/2022/12/14/BO1sMP.png)](https://zimgs.com/i/BO1sMP)


!!! hint
    openldapAs a data source, only data of specific ObjectClass under the target organization DN，User:inetOrgPerson，Organize:organizationalUnit

### Configure from Arkid synchronous data to OpenLDAP

=== "Installation plug -in"

    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the AD user data synchronization card in the plug -in rental page，Click to rent<br/>

    [![BO1nRB.png](https://v1.ax1x.com/2022/12/14/BO1nRB.png)](https://zimgs.com/i/BO1nRB)

=== "Configure ARKID as a data synchronization source server"

    [![BO163w.png](https://v1.ax1x.com/2022/12/14/BO163w.png)](https://zimgs.com/i/BO163w)

=== "Configure OpenLDAP as data synchronization client"

    [![BO1ZCO.png](https://v1.ax1x.com/2022/12/14/BO1ZCO.png)](https://zimgs.com/i/BO1ZCO)

=== "Configure OpenLDAP Client attribute mapping"
    
    [![BO1F56.png](https://v1.ax1x.com/2022/12/14/BO1F56.png)](https://zimgs.com/i/BO1F56)

    !!! hint
        openldapObjectClass created by the user is:inetOrgPerson，ObjectClass of the organization is:organizationalUnit,
        The necessary attribute of the user is SN,cn，Make sure that there are two in the data mapping，Before adding other attribute mapping
        

=== "View the source data in Arkid"
    
    [![BO1eBQ.png](https://v1.ax1x.com/2022/12/14/BO1eBQ.png)](https://zimgs.com/i/BO1eBQ)

=== "Verification data has been synchronized to OpenLDAP"
    
    [![BO1obf.png](https://v1.ax1x.com/2022/12/14/BO1obf.png)](https://zimgs.com/i/BO1obf)
