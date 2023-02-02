# data synchronization

## User data synchronization
### Features
User data synchronization is mainly to synchronize users and organizations between different systems through the SCIM protocol，Use server/Client mode，Server offers a user that meets the SCIM standard protocol，Group and other interfaces，The client side pulls the interface provided by the server through the timing task to obtain the data</br>

Classic scenes:

- ADSynchronization with Arkid
- HRSynchronization with Arkid
- HRSynchronization with AD

SCIMAgreement reference

- [RFC7643 - SCIM: Core Schema](https://tools.ietf.org/html/rfc7643)
- [RFC7644 - SCIM: Protocol](https://tools.ietf.org/html/rfc7644)
- [RFC7642 - SCIM: Definitions, Overview, Concepts, and Requirements](https://tools.ietf.org/html/rfc7642)

### Implementation
first，The implementation of the Server side SCIM protocol is implemented in the code **Scim_server** Module。</br>
in, Three important categories are:

- **scim_server.views.view_template.ViewTemplate**
    - Subclass **Scim_server.views.users_view.UsersViewTemplate**Processing user -related addition, deletion, change check
    - Subclass **Scim_server.views.groups_view.GroupsViewTemplate**Treatment of related additions, deletion, change inspection
- **scim_server.service.provider_adapter_template.ProviderAdapterTemplate**
- **scim_server.service.provider_base.ProviderBase**

SCIM ServerThe approximate process of processing the SCIM request is，**ViewTemplate**Accept request，Convert the request parameter to an object to pass it to**ProviderAdapterTemplate**，</br>
**ProviderAdapterTemplate**Verification request parameter legality，And further assemble the request object，Final call**ProviderBase**The method of processing the request object。</br>


**ScimSyncArkIDExtension**Plug -in base class inheritance**ProviderBase**，Created when plug -in load**UsersView**and**GroupsView**Separate inheritance**UsersViewTemplate**and**GroupsViewTemplate**，</br>
And register the corresponding users_url and groups_url，At this point, you only need**ProviderBase**Inherited**query_users**, **query_groups**SCIM can be implemented by other methods Server。</br>
Create SCIM Call during the server configuration**api.views.Scim_sync.create_Scim_sync**Interface processing function，Back to USERS at the same time_url and groups_URL to pick data for the client side

ClientPass through django_celery_Beat creates timing tasks，First call**api.views.Scim_sync.create_Scim_sync**The interface processing function creates the configuration of the client mode，The configuration parameters need to specify sciM Server，Used to from scim Use provided by the server_url and groups_URL pull data，</br>
Determine in the processing function to determine if it is the configuration of the CLIENT mode，Create a regular task，Pass the configuration of the client mode to Celery asynchronous task：**arkid.core.tasks.sync**, This task will eventually call [Sync] in the plug -in base class (#arkid.core.extension.Scim_sync.ScimSyncExtension.Sync) method，</br>
[sync](#arkid.core.extension.scim_sync.ScimSyncExtension.sync)Methods first will be adjusted [get_groups_users](#arkid.core.extension.Scim_sync.ScimSyncExtension.get_groups_Use) method to get Users and Groups, Then call [SYNC_groups](#arkid.core.extension.Scim_sync.ScimSyncExtension.sync_groups)
[Sync_users](#arkid.core.extension.Scim_sync.ScimSyncExtension.sync_users) to implement synchronous logic，The specific plug -in needs to cover this two methods to achieve the synchronization logic of the client side

### Abstract method
#### ServerModel abstraction method
* [create_user](#arkid.core.extension.scim_sync.ScimSyncExtension.create_user)
* [create_group](#arkid.core.extension.scim_sync.ScimSyncExtension.create_group)
* [delete_user](#arkid.core.extension.scim_sync.ScimSyncExtension.delete_user)
* [delete_group](#arkid.core.extension.scim_sync.ScimSyncExtension.delete_group)
* [replace_user](#arkid.core.extension.scim_sync.ScimSyncExtension.replace_user)
* [replace_group](#arkid.core.extension.scim_sync.ScimSyncExtension.replace_group)
* [retrieve_user](#arkid.core.extension.scim_sync.ScimSyncExtension.retrieve_user)
* [retrieve_group](#arkid.core.extension.scim_sync.ScimSyncExtension.retrieve_group)
* [update_user](#arkid.core.extension.scim_sync.ScimSyncExtension.update_user)
* [update_group](#arkid.core.extension.scim_sync.ScimSyncExtension.update_group)
* [query_users](#arkid.core.extension.scim_sync.ScimSyncExtension.query_users)
* [query_groups](#arkid.core.extension.scim_sync.ScimSyncExtension.query_groups)
#### ClientModel abstraction method
* [sync_groups](#arkid.core.extension.scim_sync.ScimSyncExtension.sync_groups)
* [sync_users](#arkid.core.extension.scim_sync.ScimSyncExtension.sync_users)
### Foundation definition

::: arkid.core.extension.scim_sync.ScimSyncExtension
    rendering:
        show_source: true
    
### Exemplary

::: extension_root.com_longgui_scim_sync_arkid.ScimSyncArkIDExtension
    rendering:
        show_source: true
        
## Permanent data synchronization
