
from django.urls import path
from . import views


urlpatterns = [
    path("arkid/saas/login", views.ArkIDLoginView.as_view(), name="login"),
    path("arkid/saas/callback", views.ArkIDCallbackView.as_view(), name="callback"),
]
