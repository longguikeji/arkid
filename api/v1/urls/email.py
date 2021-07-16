from django.conf.urls import url
from api.v1.views import email as views_email

urlpatterns = [    # pylint: disable=invalid-name
    url(r'^email/(?P<subject>[\w]+)/$', views_email.EmailClaimAPIView.as_view(), name='email'),
]
