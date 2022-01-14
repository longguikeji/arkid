from django import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.http.response import JsonResponse
from inventory.models import Tenant
from api.v1.serializers.app import AppBaseInfoSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class SubscribeAppList(views.View):

    def get(self, request, tenant_uuid, user_id):

        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = User.objects.get(uuid=user_id)
        print(user)
        data = []
        if hasattr(user, "app_subscribed_records"):
            apps_queryset = user.app_subscribed_records
            
            group_id = request.GET.get('group_id',None)
            try:
                if group_id is not None:
                    if int(group_id) != 0:
                        print(group_id)
                        from extension_root.application_group.models import ApplicationGroup
                        group = ApplicationGroup.active_objects.get(id=group_id)
                        apps_queryset = apps_queryset.filter(app__application_groups = group)
                        ApplicationGroup.objects.filter(is_del=True).delete()
                    else:
                        apps_queryset = apps_queryset.filter(Q(app__application_groups = None) | Q(app__application_groups__is_del=True))
                    
                
                apps = [record.app for record in apps_queryset.all() if (
                    not record.app.is_del and record.app.is_active)]
                data = AppBaseInfoSerializer(apps, many=True,context={"request":request}).data
            except Exception as err:
                print(err)
                data=[]

        return JsonResponse(
            data={
                "status": 200,
                "data": data
            }
        )
