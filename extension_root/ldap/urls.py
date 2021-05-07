from django.conf.urls import url
from django.urls import path
from .views import global_say_helloworld


urlpatterns = [
    path('helloworld', global_say_helloworld),
]