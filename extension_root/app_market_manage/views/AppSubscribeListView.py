from django import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.http.response import JsonResponse
from app.models import App
from extension.models import Extension
from ..models import AppSubscribeRecord
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()
from django.utils.translation import ugettext_lazy as _


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class AppSubscribeList(views.View):

    def get(self, request, tenant_uuid, user_id):
        try:
            try:
                application_group_extension = Extension.active_objects.filter(
                    type="application_group").order_by("-id").first()
                application_group_extension_is_active = application_group_extension.is_active if application_group_extension else False
            except Exception as err:
                application_group_extension_is_active = False
            
            user = User.active_objects.get(uuid=user_id)
            app_list = App.active_objects.filter(tenant__uuid=tenant_uuid)
            if application_group_extension_is_active:
                # 分组插件启用
                from extension_root.application_group.models import ApplicationGroup
                groups = ApplicationGroup.active_objects.filter(tenant__uuid=tenant_uuid).all()
                
                rs = []
                for group in groups:
                    group_app_list = group.apps.filter(tenant__uuid=tenant_uuid).all()
                    rs.append({
                        "group_name":group.name,
                        "apps":[
                            {
                                "name": app.name,
                                "id": app.uuid,
                                "value": user in app.subscribed_record.users.all() if hasattr(app,"subscribed_record") else False
                            } for app in group_app_list
                        ]
                    })
                print(app_list)
                ungroup_app_list = app_list.filter(
                    Q(application_groups = None) | Q(application_groups__is_del=True)
                ).all()
                print(ungroup_app_list)
                if ungroup_app_list.count(): 
                    rs.append(
                        {
                            "group_name": _("未分组"),
                            "apps": [
                                {
                                    "name": app.name,
                                    "id": app.uuid,
                                    "value": user in app.subscribed_record.users.all() if hasattr(app,"subscribed_record") else False
                                } for app in ungroup_app_list
                            ]
                        }
                    )
                return JsonResponse(
                    data={
                        "data": rs,
                        "application_group": application_group_extension_is_active,
                        "status": 200
                    }
                )
            else:
                # 分组插件未启用
                res_data = []
                for app in app_list.all():
                    if hasattr(app, "subscribed_record"):
                        res_data.append({
                            "name": app.name,
                            "id": app.uuid,
                            "value": user in app.subscribed_record.users.all() 
                        })
                    else:
                        record = AppSubscribeRecord(
                            app=app,
                        )
                        record.save()
                        res_data.append({
                            "name": app.name,
                            "id": app.uuid,
                            "value": False
                        })
        except Exception as err:
            print(err)
            res_data = []

        return JsonResponse(
            data={
                "data": res_data,
                "status": 200
            }
        )
