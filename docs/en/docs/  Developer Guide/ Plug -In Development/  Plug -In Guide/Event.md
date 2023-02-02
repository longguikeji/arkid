# event

Event as the core ability of plug -in and kernel communication，Completed by custom event or listening to the kernel event。

The definition of events is divided into two parts：

* [EventType: Event，Used to register (register)] (../../Reference documentation/Event list/#arkid.core.event.EventType) 
* [Event: event，Used to trigger (Dispatch)] (../../Reference documentation/Event list/#arkid.core.event.Event)


## Custom event

The general logic of the event is：

* register **Event**:  
    * [arkid.core.extension.Extension.register_event](../%20Plug -in base class/#arkid.core.extension.Extension.register_event)
    * [arkid.core.extension.Extension.register_event_type](../%20Plug -in base class/#arkid.core.extension.Extension.register_event_type)
* Listening incident:
    * [arkid.core.extension.Extension.listen_event](../%20Plug -in base class/#arkid.core.extension.Extension.listen_event)
* Incident:
    * [arkid.core.extension.Extension.dispatch_event](../%20Plug -in base class/#arkid.core.extension.Extension.dispatch_event)

!!! attention "Notice"
    When registering an event type，In order to avoid the incident TAG naming conflict，Will add the plug -in before tag **package + '.'** As a prefix

```py title='Exemplary'
from arkid.core import extension, event

CUSTOM_EVENT = 'CUSTOM_EVENT'
CUSTOM_EVENT2 = 'CUSTOM_EVENT2'

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        custom_event_tag = self.register_event(CUSTOM_EVENT, 'Custom event')
        custom_event2_tag = self.register_event_type(event.EventType(CUSTOM_EVENT2,'Custom event 2'))

        self.listen_event(custom_event_tag,event_handler)
        self.listen_event(custom_event2_tag,event_handler)

        self.register_api('/custom_event/', 'GET', self.api_func)
        self.register_api('/custom_event2/', 'GET', self.api_func2)

    def api_func(self, request):
        self.dispatch_event(event.Event(CUSTOM_EVENT))

    def api_func2(self, request):
        self.dispatch_event(event.Event(CUSTOM_EVENT2))

    def event_handler(self,event, **kwargs):
        print(event.tag)
```
## Listen to the kernel or other events

Keep the kernel events to see [Kernel event document] (../../Reference documentation/Event list/)

All events（Including the type of core and plug -in registered event type）Can [Expansion capacity-Event list] (../../../%20%20%20UserGuide/User Manual/%20Tenants Administrator/Extension/#Event list) Check



!!! attention "Notice"
    In fact，The incident defined in the plugin can also be listened to，But because the plug -in itself may not be unstable，For example, upgrades will change related events,So it is not recommended。
