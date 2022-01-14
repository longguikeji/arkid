
from django.urls import path
from . import views


urlpatterns = [
    path("wechatworkscan/login", views.WeChatWorkScanLoginView.as_view(), name="login"),
    path("wechatworkscan/callback", views.WeChatWorkScanCallbackView.as_view(), name="callback"),
    path("wechatworkscan/bind", views.WeChatWorkScanBindAPIView.as_view(), name="bind"),
    path("wechatworkscan/unbind", views.WeChatWorkScanUnBindView.as_view(), name="unbind"),
    path("wechatworkscan/userinfo", views.WeChatWorkScanUserInfoAPIView.as_view(), name="userinfo"),
]
