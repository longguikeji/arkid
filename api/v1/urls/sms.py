from django.urls import path

from api.v1.views import (
    sms as views_sms 
)

urlpatterns = [
    path('send_sms/', views_sms.SendSMSView.as_view(), name='send-sms'),
]