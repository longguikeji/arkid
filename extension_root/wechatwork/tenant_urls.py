
from django.urls import path
from . import views


urlpatterns = [
    path("wechatwork/login", views.WeChatWorkLoginView.as_view(), name="login"),
    path("wechatwork/callback", views.WeChatWorkCallbackView.as_view(), name="callback"),
    path("wechatwork/bind", views.WeChatWorkBindAPIView.as_view(), name="bind"),
    path("wechatwork/unbind", views.WeChatWorkUnBindView.as_view(), name="unbind"),
    path("wechatwork/userinfo", views.WeChatWorkUserInfoAPIView.as_view(), name="userinfo"),
]
