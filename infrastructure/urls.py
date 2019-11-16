'''
urls for infra
'''
from captcha.views import captcha_image as captcha_image_view
from django.conf.urls import url
from infrastructure.views import (
    captcha_img as captcha_view,
    sms as sms_view,
    file as file_view,
    email as email_view,
)

urlpatterns = [    # pylint: disable=invalid-name
    url(r'^captcha/image/(?P<key>\w+)/$', captcha_image_view, name='captcha-image', kwargs={'scale': 1}),
    url(r'^captcha/$', captcha_view.CaptchaAPIView.as_view(), name='captcha'),
    url(r'^sms/$', sms_view.SMSClaimAPIView.as_view(), name='common_sms'),
    url(r'^sms/(?P<subject>[\w]+)/$', sms_view.SMSClaimAPIView.as_view(), name='sms'),
    url(r'^email/(?P<subject>[\w]+)/$', email_view.EmailClaimAPIView.as_view(), name='email'),
    url(r'^file/$', file_view.FileCreateAPIView.as_view(), name='upload_file'),
    url(r'^file/(?P<filename>[\w|\.]+)$', file_view.FileAPIView.as_view(), name='download_file'),
]
