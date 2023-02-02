# API

ArkIDBased on django-ninja framework to develop API，Fully inherited all its abilities。

## Custom API

able to pass**Django-ninja**and **Django native** Two ways are defined API。

The main difference is，Django-Ninja method definition will automatically appear in Openapi.During JSON,And depend on schema，Django native will not or need。

### Django-ninja of API Definition

use [arkid.core.extension.Extension.register_api](../%20 plug -in base class/#arkid.core.extension.Extension.register_api)


#### Create SCHEMA

use [arkid.core.extension.create_extension_schema](../%20 plug -in base class/#arkid.core.extension.create_extension_schema)

Notice！The second parameter of this function，Refers to the plug -in \_\_init\_\_.py Directory where the file is located

```py title='Exemplary'
from arkid.core import extension

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_api('/path/', 'GET', self.api_func)

    def api_func(self, request):
        pass
```
#### Authority
{todo}

#### Pagination

arkidProvide the basic pagoe function，The method of use is as follows：

``` py title="Pagination"
...
from ninja.pagination import paginate #Introduce paging decorative device
from arkid.core.pagenation import CustomPagination #Introduction to the paging device
...


# Declaration returns the column table structure
class AppGroupListItemOut(Schema):
    id:str
    name:str
# State the return structure
class AppGroupListOut(ResponseSchema):
    data: List[AppGroupListItemOut]

@api.get("/path/", response=List[AppGroupListItemOut]) #Notice Here  Therefore
@operation(AppGroupListOut)
@paginate(CustomPagination)
def get_app_groups(request,tenant_id: str):
    """ Application group list
    """
    groups = AppGroup.expand_objects.filter(tenant__id=tenant_id)
    parent_id = query_data.dict().get("parent_id",None)
    groups = groups.filter(parent__id=parent_id)
    return groups.all()
```





### Django of API Definition

use [arkid.core.extension.Extension.register_routers](../%20 plug -in base class/#arkid.core.extension.Extension.register_routers)

```py title='Exemplary'
from arkid.core import extension
from django.urls import re_path
from django

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        class CaseView(View):
            def post(self,request):
                pass

        path_list = [
            re_path(rf'^/path/$',self.api_func),
            re_path(rf'^/path2/$',CaseView.as_view()),
        ]
        self.register_routers(path_list)

    def api_func(self,request):
        pass
```
## Modify the kernel API

When necessary，We need to change the API in the original kernel。

### Modify Request

Modify Request，Just modify API -related Request Schema.

after，We want to get the request，And execute custom logic.

Before each API response，Will throw a event，Event tag is: **operation_id + '_pre'**, Listen to the incident to get the Request object

!!! hint
    operation_id allowable openapi.json Look at

use 

* [arkid.core.extension.Extension.register_extend_api](../%20Plug -in base class/#arkid.core.extension.Extension.register_extend_api)
* [arkid.core.extension.Extension.listen_event](../%20Plug -in base class/#arkid.core.extension.Extension.listen_event)


```py title='Exemplary'
from arkid.core import extension
from api.v1.views.app import AppConfigSchemaIn

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_extend_api(AppConfigSchemaIn, case1=str, case2=(str, Field(title='case2_name')))
        self.listen_event('api_v1_views_app_list_apps_pre',self.app_list_pre_handler)

    def app_list_pre_handler(self,event,**kwargs):
        print(event.request.case1)
        print(event.request.case2)
```

### Modify response

Modify response，In addition to modifying Response Other than Schema，It also needs to really change the final return value

After the response of each API is complete，Will also throw a event，The tag of the event is operation_id， Just listen to the incident and modify the reponse in the incident。

use 

* [arkid.core.extension.Extension.register_extend_api](../%20Plug -in base class/#arkid.core.extension.Extension.register_extend_api)
* [arkid.core.extension.Extension.listen_event](../%20Plug -in base class/#arkid.core.extension.Extension.listen_event)

```py title='Exemplary'
from arkid.core import extension
from api.v1.views.app import AppConfigSchemaOut

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_extend_api(AppConfigSchemaOut, case1=str, case2=(str, Field(title='case2_name')))
        self.listen_event('api_v1_views_app_list_apps',self.app_list_handler)

    def app_list_pre_handler(self,event,**kwargs):
        event.response['case1'] = 'case1'
        event.response['case2'] = 'case2'
```
