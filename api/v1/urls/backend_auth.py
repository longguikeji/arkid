from django.urls import path

from api.v1.views import backend_auth

urlpatterns = [
    path(
        'backend_auth/', backend_auth.BackendAuthView.as_view(), name='backend-auth'
    ),
]