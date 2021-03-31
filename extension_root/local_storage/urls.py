# from django.conf.urls.static import static
from .constants import KEY
from config import get_app_config
from django.urls import re_path
from django.views.static import serve
import re

c = get_app_config()

data_path = c.extension.load_from_db(KEY).get('data_path')

urlpatterns = [
    re_path(r'^%s(?P<path>.*)$' % re.escape('/upload/render/'.lstrip('/')), serve, name='render', kwargs = {
        'document_root': data_path,
    }),
]
