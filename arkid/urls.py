"""arkid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from arkid.core.api import api as core_api
from api import v1
from arkid.login import view as login_view
from arkid.core import urls as core_urls
from arkid.redoc import view as redoc_view
from scim_server import urls as scim_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", core_api.urls),
    path("api/v1/login", login_view.LoginEnter.as_view()),
    path("api/v1/login_process", login_view.LoginProcess.as_view()),
    path("api/v1/redoc", redoc_view.Redoc.as_view()),
    path("api/v1/openapi_redoc.json", redoc_view.RedocOpenAPI.as_view()),
]

urlpatterns += core_urls.urlpatterns
urlpatterns += scim_urls.urlpatterns
