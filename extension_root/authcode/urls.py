# from django.conf.urls.static import static
from .constants import KEY
from config import get_app_config
from django.urls import re_path
from django.views.static import serve
import re

c = get_app_config()

upload_file_path = c.extension.load_from_db(KEY).get('upload_file_path')

urlpatterns = [
    re_path(r'^%s(?P<path>.*)$' % re.escape('/authcode/render/'.lstrip('/')), serve, name='render', kwargs={
        'document_root': upload_file_path,
    }),
]
