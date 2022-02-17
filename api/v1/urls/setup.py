from django.urls import path

from api.v1.views import (
    setup as views_setup
)

urlpatterns = [
    path('get_frontendurl/', views_setup.GetFrontendUrlAPIView.as_view(), name='get-frontendurl'),
    path('set_frontendurl/', views_setup.SetFrontendUrlAPIView.as_view(), name='set-frontendurl'),
]
