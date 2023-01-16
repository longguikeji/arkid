# ArkID User data synchronous plugin

## Features
1. ServerThe mode implements the user and organization in Arkid through the standard SCIM interface
2. ClientThe mode is implemented. Users and organizations in Server


### Create Arkid Synchronous server

=== "Open**Identity authentication source->SCIM data synchronization**page， Click to create"
    [![X7bu80.png](https://s1.ax1x.com/2022/06/16/X7bu80.png)](https://imgtu.com/i/X7bu80)

=== "Configuration form parameter"
    [![X7Xg0S.png](https://s1.ax1x.com/2022/06/16/X7Xg0S.png)](https://imgtu.com/i/X7Xg0S)

### Create Arkid Synchronous client

=== "Open**Identity authentication source->SCIM data synchronization**page"
    Click to create
    [![X7bu80.png](https://s1.ax1x.com/2022/06/16/X7bu80.png)](https://imgtu.com/i/X7bu80)

=== "Configuration form parameter"
    The following configuration indicates that the timing synchronization task runs every 10 minutes
    [![X7qhf1.png](https://s1.ax1x.com/2022/06/16/X7qhf1.png)](https://imgtu.com/i/X7qhf1)


## Implementation
Abstract methods to cover the base class of plug -in，See [ARKID.core.extension.Scim_sync.ScimSyncExtension](../../%20%20 Developer Guide/%20 plug -in classification/data synchronization/)

## Abstract method implementation:
#### ServerModel abstraction method
* [query_users](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.query_users)
* [query_groups](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.query_groups)
#### ClientModel abstraction method
* [sync_groups](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.sync_groups)
* [sync_users](#extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension.sync_users)

## Code

::: extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension
    rendering:
        show_source: true
