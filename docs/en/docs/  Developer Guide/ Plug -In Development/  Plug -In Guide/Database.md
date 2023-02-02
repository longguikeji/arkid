# database

## Custom data table

The plug -in can have its own data table，Just create Models in the root directory.py file，Use django ORM standard writing。

Plug -in database version update is also the principle of Django，Developers need to run by themselves**makemigrations**

migrateWill run automatically before loading the plug -in

```py title='models.py'
from django.db import models
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig

app_label = "com_longgui_case"

class CaseApp(AppConfig):
    name = app_label
    
class CaseModel(models.Model):
    class Meta:
        app_label = app_label
    
    nickname = models.CharField(verbose_name=_('nickname', 'Nick name'), max_length=128)
```
!!! info "hint"
    In Models.Be sure to declare AppConfig in PY， When creating a model, you also need to declare its app_label

    makemigrations command: 
    
    `python manage.py makemigrations {app_label}`


## Extended kernel data table

In Arkid.core.The data table defined in the models，All inherit ExtendModel Category，It's all modified modes that can be directly expanded。

The Model class that is recommended to expand is：

* [arkid.core.models.Tenant](../../Reference documentation/Data table definition/#arkid.core.models.Tenant)
* [arkid.core.models.User](../../Reference documentation/Data table definition/#arkid.core.models.User)
* [arkid.core.models.UserGroup](../../Reference documentation/Data table definition/#arkid.core.models.UserGroup)
* [arkid.core.models.App](../../Reference documentation/Data table definition/#arkid.core.models.App)
* [arkid.core.models.AppGroup](../../Reference documentation/Data table definition/#arkid.core.models.AppGroup)

In the plug -in，Define a model，The outside key is the above classes。To facilitate this operation，exist**arkid.core.models**These abstract classes have been defined in China，Can be inherited directly。

* [arkid.core.expand.TenantExpandAbstract](../../Reference documentation/Data table definition/#arkid.core.models.TenantExpandAbstract)
* [arkid.core.expand.UserExpandAbstract](../../Reference documentation/Data table definition/#arkid.core.models.UserExpandAbstract)
* [arkid.core.expand.UserGroupExpandAbstract](../../Reference documentation/Data table definition/#arkid.models.expand.UserGroupExpandAbstract)
* [arkid.core.expand.AppExpandAbstract](../../Reference documentation/Data table definition/#arkid.core.models.AppExpandAbstract)
* [arkid.core.expand.AppGroupExpandAbstract](../../Reference documentation/Data table definition/#arkid.models.expand.AppGroupExpandAbstract)

After defining the model，Need to call **[arkid.core.extension.Extension.register_extend_field]()** register，After that, you can directly query，keep，Delete operation

* **Inquire**: {model}.expand_objects
* **New or modified**: {model}.save()
* **delete**: {model}.delete()

```py title='models.py'
from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_case"

class LongguiCaseAppConfig(AppConfig):
    name = app_label
    
class CaseUser(UserExpandAbstract):
    class Meta:
        app_label = app_label
    
    nickname = models.CharField(verbose_name=_('nickname', 'Nick name'), max_length=128)
```

```py title='__init__.py'
from arkid.core import extension 
from arkid.core.translation import gettext_default as _
from arkid.core.models import User
from .models import CaseUser
from typing import List, Optional
from pydantic import Field

package = 'com.longgui.case'

UserSchema = extension.create_extension_schema(
    'UserSchema',
    package,
    fields=[
        ('username', str, Field()),
        ('nickname', Optional[str], Field()),
    ]
)

class CaseExtension(extension.Extension):
    def load(self):
        super().load()
        self.register_extend_field(CaseUser, 'nickname')
        self.register_api('/test/', 'POST', self.post_handler, tenant_path=True)
        self.register_api('/test/', 'GET', self.get_handler, response=List[UserSchema], tenant_path=True)

    def post_handler(self, request, tenant_id:str, data:UserSchema):
        tenant = request.tenant
        user = User()
        user.tenant = tenant
        user.username = data.username
        user.nickname = data.nickname
        user.save()

    def get_handler(self, request, tenant_id:str, ):
        users = User.expand_objects.filter(tenant=request.tenant).all()
        return list(users)
    
extension = CaseExtension(
    package=package,
    description="",
    version='1.0',
    labels='case',
    homepage='https://www.longguikeji.com',
    logo='',
    author='wely',
)
```
