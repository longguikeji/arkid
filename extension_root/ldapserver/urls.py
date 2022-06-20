"""
插件路由
"""

from django.urls import re_path
from .views import Search,Login

urlpatterns = [
    re_path(
        r'ldap/search/',
        Search.as_view(),
        name="search"
    ),
    re_path(
        r'ldap/login/',
        Login.as_view(),
        name="login"
    )
]
