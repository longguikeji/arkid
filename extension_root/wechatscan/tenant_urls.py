
from django.urls import path
from . import views


urlpatterns = [
    path("wechatscan/login", views.WeChatScanLoginView.as_view(), name="login"),
    path("wechatscan/callback", views.WeChatScanCallbackView.as_view(), name="callback"),
    path("wechatscan/bind", views.WeChatScanBindAPIView.as_view(), name="bind"),
    path("wechatscan/unbind", views.WeChatScanUnBindView.as_view(), name="unbind"),
    path("wechatscan/userinfo", views.WeChatScanUserInfoAPIView.as_view(), name="userinfo"),
]
