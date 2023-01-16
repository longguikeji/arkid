# multi-language

Because django-Ninja's original multi -language interface compatibility with Django in OpenAPI's interface is not good。

so，Arkid customized a set of multi -language implementation methods。

Mainly through：

[arkid.core.translation.gettext_default](../../Reference documentation/%20 kernel API/#arkid.core.translation)

To implement，The default is”Simplified Chinese“。

```py
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
