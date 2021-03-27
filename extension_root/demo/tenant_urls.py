from django.conf.urls import url
from django.urls import path
from .views import tenant_say_helloworld


urlpatterns = [
    path('helloworld', tenant_say_helloworld),
]