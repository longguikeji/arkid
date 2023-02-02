# Database user and organization data synchronous plug -in

## Features
1. ServerThe mode implements the user and organization in the database server through the standard SCIM interface
2. ClientThe mode is implemented. Users and organizations in Server, Synchronous to the client database
3. This plugin only supports MySQL and SQLServer for the time being

## Configure two MYSQL database database synchronization

### Create two databases and tables

- Create a Server database that provides synchronous data，Establish**sync_users**, **sync_groups**surface， And the intermediate table of the Groups of user**sync_users_groups_rel**, </br>
**sync_users_groups_rel**User in the middle table_ID key associated SYNC_users(id)， group_ID key associated SYNC_groups(id)
    
    !!! hint
        In this example, the relationship between the User and Group is the relationship between Manytomany, If the user belongs to only one group，allowable**sync_users**Definition group in the table_id，Outer key associated SYNC_groups(id)

- Create a client database，Used to synchronize the data provided by the server database to the Client database

    !!! Notice
        Convenient for demonstration，The table definition in the client database is the same as the Server database,The actual production environment may be different

### Configuration Mysql Source database

=== "Open**SCIM data synchronization**page，Click to create"
    [![BjpL33.png](https://v1.ax1x.com/2023/01/03/BjpL33.png)](https://zimgs.com/i/BjpL33)

=== "Configuration form parameter"

    [![Bjp05j.png](https://v1.ax1x.com/2023/01/03/Bjp05j.png)](https://zimgs.com/i/Bjp05j)

    !!! hint
        If the user and group are more paired，Need to be filled in**User table group outer key field** </br>
        If the user and group are more to the relationship，Need to be filled in**Users and organizations are more to multi -relationship tables**， **User Organic Relationship Table User outer key field**， **User Organic Relationship Form Group outer key field**</br>
        groupThe fields associated between superiors need to be set up**Organization table Parent outer key field**</br>
        Targets must exist in user and organizational attribute mapping lists_ATTR is a mapping of ID, The ID of the user and group in the SCIM protocol here

=== "Configure user attribute mapping"

    [![Bjp3C5.png](https://v1.ax1x.com/2023/01/03/Bjp3C5.png)](https://zimgs.com/i/Bjp3C5)

=== "Configuration tissue attribute mapping"

    [![Bjp7Bm.png](https://v1.ax1x.com/2023/01/03/Bjp7Bm.png)](https://zimgs.com/i/Bjp7Bm)

### Configure from the source database synchronous data to the client database

=== "Open**SCIM data synchronization**page, Click to create"

    [![BjpL33.png](https://v1.ax1x.com/2023/01/03/BjpL33.png)](https://zimgs.com/i/BjpL33)


=== "Configuration Mysql Synchronous client"

    [![BjpEb4.png](https://v1.ax1x.com/2023/01/03/BjpEb4.png)](https://zimgs.com/i/BjpEb4)

    !!! hint
        If the user and group are more paired，Need to be filled in**User table group outer key field** </br>
        If the user and group are more to the relationship，Need to be filled in**Users and organizations are more to multi -relationship tables**， **User Organic Relationship Table User outer key field**， **User Organic Relationship Form Group outer key field**</br>
        groupThe fields associated between superiors need to be set up**Organization table Parent outer key field**</br>
        Source must exist in the user and organizational attribute mapping list_ATTR is a mapping of ID，Used to match the data in the Server and Client database, Determine whether the data has been synchronized


### View server database table data

=== "View source database Groups"
    
    [![BjpQRh.png](https://v1.ax1x.com/2023/01/03/BjpQRh.png)](https://zimgs.com/i/BjpQRh)

=== "View source database users"
    
    [![BjpNZ9.png](https://v1.ax1x.com/2023/01/03/BjpNZ9.png)](https://zimgs.com/i/BjpNZ9)

=== "View source database users and groups relationship data"
    
    [![BjpuqY.png](https://v1.ax1x.com/2023/01/03/BjpuqY.png)](https://zimgs.com/i/BjpuqY)


### View the client database table data

=== "Check the client database Groups"
    
    [![BjpwDH.png](https://v1.ax1x.com/2023/01/03/BjpwDH.png)](https://zimgs.com/i/BjpwDH)

=== "Check the client database users"
    
    [![BjpyMZ.png](https://v1.ax1x.com/2023/01/03/BjpyMZ.png)](https://zimgs.com/i/BjpyMZ)

=== "Check the relationship data of the CLIENT database users and groups"
    
    [![BjpK3U.png](https://v1.ax1x.com/2023/01/03/BjpK3U.png)](https://zimgs.com/i/BjpK3U)
