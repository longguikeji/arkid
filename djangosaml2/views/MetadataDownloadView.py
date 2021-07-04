from django.http import HttpResponse
from django.views import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from six import text_type
from app.models import App

@method_decorator(never_cache, name="dispatch")
class MetadataDownload(View):

    def get(self,request,tenant_uuid,app_id):
        app = App.active_objects.filter(id=app_id)
        meta_data = open(app.data["metadata_file_path"],"r").read()
        res = HttpResponse(content=text_type(meta_data).encode('utf-8'), content_type="application/octet-stream")
        res['Content-Disposition'] = 'attachment;filename="idp_metadata.xml"'
        return res
