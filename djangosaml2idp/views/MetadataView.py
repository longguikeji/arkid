import os
from django.http import HttpResponse
from django.views import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from app.models import App
from six import text_type

@method_decorator(never_cache, name="dispatch")
class Metadata(View):

    def get(self,request,tenant_uuid,app_id):
        app = App.active_objects.get(id=app_id)
        meta_data = open(app.data["metadata_file_path"],"r").read()
        return HttpResponse(content=text_type(meta_data).encode('utf-8'), content_type="text/xml; charset=utf8")