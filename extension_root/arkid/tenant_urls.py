from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    path("arkid/login", views.ArkIDLoginView.as_view(), name="login"),
    path("arkid/callback", views.ArkIDCallbackView.as_view(), name="callback"),
    path("arkid/bind", views.ArkIDBindAPIView.as_view(), name="bind"),
    # path(
    #     "gitee/register/bind",
    #     views.GiteeRegisterAndBindView.as_view(),
    #     name="register_bind",
    # ),
]
