from django.conf.urls import url
from django.urls import re_path
from django.urls.conf import path
# dev
from djangosaml2.views.dev import IndexView

# sso
from djangosaml2.views.SSOEntryView import SSOEntry
from djangosaml2.views.MetadataView import Metadata
from djangosaml2.views.MetadataDownloadView import MetadataDownload
from djangosaml2.views.SSOResponseView import SSOResponse


urlpatterns = [
    re_path(r'saml2idp/(?P<app_id>[\w-]+)/dev/index/', IndexView.as_view(), name='dev_index'),
    re_path(r'saml2idp/(?P<app_id>[\w-]+)/sso/post/', SSOEntry.as_view(), name="login_post"),
    re_path(r'saml2idp/(?P<app_id>[\w-]+)/sso/redirect/', SSOEntry.as_view(), name="login_redirect"),
    re_path(r'saml2idp/(?P<app_id>[\w-]+)/sso/response/', SSOResponse.as_view(), name="response"),
    re_path(r'saml2idp/(?P<app_id>[\w-]+)/metadata/', Metadata.as_view(), name='metadata'),
    re_path(r'saml2idp/(?P<app_id>[\w-]+)/download/metadata/', MetadataDownload.as_view(), name='download_metadata'),

]