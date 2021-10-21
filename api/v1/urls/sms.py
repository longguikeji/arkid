from django.urls import path

from api.v1.views import sms as views_sms
from django.conf.urls import url

urlpatterns = [
    # path('send_sms/', views_sms.SendSMSView.as_view(), name='send-sms'),
    url(r'^sms/$', views_sms.SMSClaimAPIView.as_view(), name='send-sms'),
    url(r'^sms/(?P<subject>[\w]+)/$', views_sms.SMSClaimAPIView.as_view(), name='sms'),
]
