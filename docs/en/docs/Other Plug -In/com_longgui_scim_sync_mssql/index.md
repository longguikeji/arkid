# SQL Server User data synchronous plugin

## Features
1. ServerThe pattern implements the SQL through the standard SCIM interface Users and organizations in the Server database
2. ClientThe mode is implemented. Users and organizations in Server, Synchronous to SQL In Server database

## Configure two SQL Synchronous database between the Server database

### Create two databases and tables

- Create a Server database that provides synchronous data，Establish**users**, **groups**surface， And the intermediate table of the Groups of user**users_groups**, </br>
**users_groups**User in the middle table_ID key associated Users (ID)， group_ID key associated Groups (ID)
    
    !!! hint
        In this example, the relationship between the User and Group is the relationship between Manytomany, If the user belongs to only one group，allowable**users**Definition group in the table_id，GROUPS (ID)

- Create a client database，Used to synchronize the data provided by the server database to the Client database

    !!! Notice
        Convenient for demonstration，The table definition in the client database is the same as the Server database,The actual production environment may be different

### Configure SQL Server Source database

=== "Open**SCIM data synchronization**page，Click to create"
    [![vgGHo9.png](https://s1.ax1x.com/2022/08/24/vgGHo9.png)](https://imgse.com/i/vgGHo9)

=== "Configuration form parameter"

    [![vTz36J.png](https://s1.ax1x.com/2022/09/05/vTz36J.png)](https://imgse.com/i/vTz36J)

    !!! hint
        If the user and group are more paired，Need to be filled in**User table group outer key field** </br>
        If the user and group are more to the relationship，Need to be filled in**Users and organizations are more to multi -relationship tables**， **User Organic Relationship Table User outer key field**， **User Organic Relationship Form Group outer key field**</br>
        groupThe fields associated between superiors need to be set up**Organization table Parent outer key field**</br>
        Targets must exist in user and organizational attribute mapping lists_ATTR is a mapping of ID, The ID of the user and group in the SCIM protocol here


### Configure from the source database synchronous data to the client database

=== "Open**SCIM data synchronization**page, Click to create"
    [![vgGHo9.png](https://s1.ax1x.com/2022/08/24/vgGHo9.png)](https://imgse.com/i/vgGHo9)


=== "Configure SQL Server synchronization client"

    [![vTzTns.png](https://s1.ax1x.com/2022/09/05/vTzTns.png)](https://imgse.com/i/vTzTns)

    !!! hint
        If the user and group are more paired，Need to be filled in**User table group outer key field** </br>
        If the user and group are more to the relationship，Need to be filled in**Users and organizations are more to multi -relationship tables**， **User Organic Relationship Table User outer key field**， **User Organic Relationship Form Group outer key field**</br>
        groupThe fields associated between superiors need to be set up**Organization table Parent outer key field**</br>
        Source must exist in the user and organizational attribute mapping list_ATTR is a mapping of ID，Used to match the data in the Server and Client database, Determine whether the data has been synchronized


### View server database table data

=== "View source database Groups"
    
    [![v7ST2D.png](https://s1.ax1x.com/2022/09/05/v7ST2D.png)](https://imgse.com/i/v7ST2D)

=== "View source database users"
    
    [![v7SbKH.png](https://s1.ax1x.com/2022/09/05/v7SbKH.png)](https://imgse.com/i/v7SbKH)

=== "View source database users_groups"
    
    [![v7SXVI.png](https://s1.ax1x.com/2022/09/05/v7SXVI.png)](https://imgse.com/i/v7SXVI)


### View the client database table data

=== "Check the client database Groups"
    
    [![v7Sqrd.png](https://s1.ax1x.com/2022/09/05/v7Sqrd.png)](https://imgse.com/i/v7Sqrd)

=== "Check the client database users"
    
    [![v7SLqA.png](https://s1.ax1x.com/2022/09/05/v7SLqA.png)](https://imgse.com/i/v7SLqA)

=== "Check the client database users_groups"
    
    [![v7S7xe.png](https://s1.ax1x.com/2022/09/05/v7S7xe.png)](https://imgse.com/i/v7S7xe)
