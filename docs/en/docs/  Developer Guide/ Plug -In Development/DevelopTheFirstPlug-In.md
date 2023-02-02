# Develop the first plug -in

## Create a plug -in directory and file
cloneUnder ARKID's git warehouse，Find in the root directory **arkid.toml** document
turn up extension item，The file location of the configuration indicator plugin，as follows：
```toml
[extension]
root = ["./extension_root", "./my_extensions"]
```

exist **my_extensions** New folder in the directory，named：**com_company_type_helloworld**

!!! Notice
    The file name of the plug -in directory should completely correspond to its Package，Just put the symbol point of Package '**.**' Change to the bottom line'**_**'

In a folder com_company_type_helloworld Down，create a new file**\_\_init\_\_.py**

In this way, the main directory of the plugin and the main file are completed。

## Write plug -in code (parsing by line by line)

exist **\_\_init\_\_.py** Insert the following code in the file：

```python linenums="1"

from arkid.core import extension,api,event  # (1)
from pydantic import Field

HELLOWORLD = 'HELLOWORLD' # (2)
package = 'com.company.type.helloworld' # (3)

HelloworldOutSchema = extension.create_extension_schema( # (11)
    'HelloworldOutSchema',
    package,
    fields = [
        ('data',str,Field())
    ]
)

class HelloworldExtension(extension.Extension): # (4)
    def load(self): # (5)
        super().load()
        
        self.register_api( # (10)
            '/helloworld_api/', 'GET', self.helloworld_api, 
            tags=['helloworld'], response=HelloworldOutSchema
        )
        
        hellowold_event_tag = self.register_event(HELLOWORLD, 'helloworld') # (6)
        self.listen_event(hellowold_event_tag, self.helloworld) # (7)

    def helloworld_api(self, request):
        event_results = event.dispatch_event(event.Event(package+'.'+HELLOWORLD, tenant=None, data='helloworld')) # (12)
        for fun, (result, ext) in event_results:
            return {'data':result}
        
    def helloworld(self, event, **kwargs): # (8)
        print(event.data) # (9)
        return event.data

extension = HelloworldExtension( # (13)
    package=package,
    description='my first extension',
    version='1.0',
    labels='hellowworld',
    homepage='https://arkid.cc',
    logo='',
    author='your-name@your-company.com',
)
```

1. ArkIDThe kernel code is in Arkid.Core in this package, extension (various base classes related to plugins), API (encapsulated ninja API object), Event (all objects and methods related to the event)
2. Event tag
3. Package of the plug -in, Because of repeatedly，Should be defined alone
4. Define plug -in，Inherit the most basic plug -in base class Extension
5. load() Abstract method，The core startup method of all plug -in，Must be realized
6. Registration event in the plug -in，In order to make the TAG naming conflict，Will add in front of the passing tag **package+'.'** Prefix
7. Add the callback function of the listening event
8. Define the callback function
9. Print the data parameter of Event
10. Define a API，Reference django-Ninja related documents
11. Define the SCHEMA of the API，In order to avoid naming conflicts，Can only be via extension.create_extension_schema method
12. Throw an incident，Note that the tag of the event is to add the prefix part
13. Single object that generates the plugin，Arkid will get__init__.The extension object in the py file as the main body of the plugin

## Load and start plug -in

Start django

``` shell

python manager.py runserver
```
ArkIDWill according to Arkid.Configuration in TOML file，Automatically load all plug -in in turn in all plug -in directory，And print out loading information。


``` shell

Importing  my_extension/com_company_type_helloworld   
xxxx-xx-xx 03:21:57,944 - arkid - INFO - Imported  <module 'my_extension.com_company_type_helloworld' from '/arkid/my_extension/com_company_type_helloworld/__init__.py'>   
xxxx-xx-xx 03:21:57,944 - arkid - INFO - my_extension.com_company_type_helloworld import success   
```
After loading successfully，If the plug -in is enabled，Will call it**load()**function， Complete the startup，The start success will be printed and the following content will be printed：

``` shell

2022-xx-xx 03:22:00,993 - arkid - INFO - my_extension.com_company_type_helloworld load success  
```

## Check and test plug -in

access:

``` shell
http://{ArkID host}/api/redoc#tag/helloworld/operation/my_extension_com_company_type_helloworld_helloworld
```

You can see that the API defined in the plug -in will be displayed in the documentation，
Try to call the interface，Can get printing：
``` shell

helloworld
[xx/xx/xxxx 03:22:07] "GET /api/v1/tenant/{tenant_id}/helloworld/ HTTP/1.1" 200 4
```
!!! hint
    Interface **tenant_id** allowable [Tenant management-Practice configuration](../../../%20%20%20UserGuide/User&20Manual/%20Tenants%20Administrator/Tenant%20Management/) See

