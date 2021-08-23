"""
插件路由
"""

from django.urls import re_path
from .views import Search

urlpatterns = [
    re_path(
        r'ldap/search/',
        Search.as_view(),
        name="search"
    )
]
