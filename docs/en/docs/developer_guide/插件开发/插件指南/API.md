# API

ArkID develops APIs based on the django-ninja framework, inheriting all of its capabilities in full.

## Custom API

You can customize the API in ** Django-ninja ** two ways: and ** Django native **.

The main difference is that django-ninja style definitions automatically appear in the openapi. JSON and depend on the Schema, while native Django does not or does not need to.

### Django-ninja's API definition approach

Use [ arkid.core.extension.Extension.register_api ](../%20插件基类/#arkid.core.extension.Extension.register_api)


#### Create a Schema

Use [ arkid.core.extension.create_extension_schema ](../%20插件基类/#arkid.core.extension.create_extension_schema)

Notice! The second parameter of this function refers to the directory where the \ _ \ _ init \ _ \ _. Py file of the plug-in is located.

```py title='示例'
from arkid.core import extension

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_api('/path/', 'GET', self.api_func)

    def api_func(self, request):
        pass
```
#### Permissions
{todo}

#### Paging

The arkid provides the basic pager function, which is used as follows:

``` py title="分页"
...
from ninja.pagination import paginate #引入分页装饰器
from arkid.core.pagenation import CustomPagination #引入分页器
...


# 声明返回列表项结构
class AppGroupListItemOut(Schema):
    id:str
    name:str
# 声明返回结构体
class AppGroupListOut(ResponseSchema):
    data: List[AppGroupListItemOut]

@api.get("/path/", response=List[AppGroupListItemOut]) #注意 此处因分页器会自动封装错误提示等数据  故而此处不需要填写封装错误信息后的Schema
@operation(AppGroupListOut)
@paginate(CustomPagination)
def get_app_groups(request,tenant_id: str):
    """ 应用分组列表
    """
    groups = AppGroup.expand_objects.filter(tenant__id=tenant_id)
    parent_id = query_data.dict().get("parent_id",None)
    groups = groups.filter(parent__id=parent_id)
    return groups.all()
```





### How Django's API is defined

Use [ arkid.core.extension.Extension.register_routers ](../%20插件基类/#arkid.core.extension.Extension.register_routers)

```py title='示例'
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

When necessary, we need to change the API in the original kernel.

### Modify the request

To modify the request is to modify the API-related Request Schema.

After that, we want to get the request and execute the custom logic.

Before each API response, an event is thrown, the event tag is: ** operation_id + '_pre' **, and the request object is obtained by listening to the event.

!!! Hint

Use

* [Arkid. Core. Extension. Extension. Register _ extend _ API] (./% 20 plugin base class/# arkid. Core. Extension. Extension. Register _ extend _ API)
* [Arkid. Core. Extension. Extension. Listen _ event] (./% 20 plugin base class/# arkid. Core. Extension. Extension. Listen _ event)


```py title='示例'
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

### Modify the response

To modify the response, in addition to modifying the Response Schema, you need to actually change the final return value.

After each API response is completed, an event will also be thrown. The tag of the event is operation _ ID. Listen to the event and modify the reponse in the event.

Use

* [Arkid. Core. Extension. Extension. Register _ extend _ API] (./% 20 plugin base class/# arkid. Core. Extension. Extension. Register _ extend _ API)
* [Arkid. Core. Extension. Extension. Listen _ event] (./% 20 plugin base class/# arkid. Core. Extension. Extension. Listen _ event)

```py title='示例'
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