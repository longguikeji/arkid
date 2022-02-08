from common.provider import ApplicationManageProvider

class ApplicationMarketManageProvider(ApplicationManageProvider):
    
    def get_queryset(self, objs, view_instance, *args, **kwargs):
        return [ obj for obj in objs if view_instance.request.user in obj.subscribed_record.users.all()]
    
    def list_view(self,request,rs,*args, **kwargs):
        rs.data["app_manage"]=True
        return rs