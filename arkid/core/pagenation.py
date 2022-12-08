from typing import Any, List, Optional
from django.http import QueryDict
from ninja.pagination import PaginationBase
from ninja import Field, Schema
from arkid.core.schema import ResponseSchema



class CustomPagination(PaginationBase):
    class Input(Schema):
        page: int = Field(
            default=1
        )

        page_size: int = Field(
            default=10
        )

    class Output(ResponseSchema):
        items: Optional[List[Any]] = Field(
            default=[]
        )
        count: Optional[int]
        previous: Optional[str]
        next: Optional[str]

    def paginate_queryset(self, queryset, pagination: Input, request, **params):
        
        if isinstance(queryset,dict) and "error" in queryset.keys() and queryset.get("error") not in ["0",0]:
            queryset["items"] = []
            return queryset
        
        page = pagination.page
        page_size = pagination.page_size
        items = list(queryset)[max(page-1,0)*page_size : page*page_size]
        return {
            'items': items,
            'count': len(list(queryset)),
            "previous": f"{request.path}?page={page-1}&page_size={page_size}" if page >= 2 else "",
            "next": f"{request.path}?page={page+1}&page_size={page_size}" if page * page_size < len(list(queryset)) else ""
        }


class ArstorePagination(CustomPagination):
    def paginate_queryset(self, queryset, pagination: CustomPagination.Input, request, **params):
        
        if isinstance(queryset,dict) and "error" in queryset.keys() and queryset.get("error") not in ["0",0]:
            queryset["items"] = []
            return queryset
        
        page = pagination.page
        page_size = pagination.page_size
        items = queryset["items"]
        count = queryset["count"]

        return {
            'items': items,
            'count': count,
            "previous": f"{request.path}?page={page-1}&page_size={page_size}" if page >= 2 else "",
            "next": f"{request.path}?page={page+1}&page_size={page_size}" if page * page_size < count else ""
        }


class ArstoreExtensionPagination(CustomPagination):
    def paginate_queryset(self, queryset, pagination: CustomPagination.Input, request, **params):

        if isinstance(queryset,dict) and "error" in queryset.keys() and queryset.get("error") not in ["0",0]:
            queryset["items"] = []
            return queryset

        page = pagination.page
        page_size = pagination.page_size
        items = queryset["items"]
        count = queryset["count"]

        from arkid.extension.models import Extension
        installed_exts = Extension.valid_objects.filter()
        installed_ext_packages = {ext.package: ext for ext in installed_exts}
        for ext in items:
            ext['arkstore_uuid'] = ext['uuid']
            if ext['package'] in installed_ext_packages:
                local_ext = installed_ext_packages[ext['package']]
                ext['local_uuid'] = str(local_ext.id)
                if local_ext.version < ext['version']:
                    ext['has_upgrade'] = True
            else:
                ext['local_uuid'] = None
                ext['installed'] = False

        tenant = request.tenant
        if tenant.is_platform_tenant:
            # for ext in items:
            #     ext["lease_useful_life"] = ["不限天数，不限人数"]
            #     ext["lease_state"] = '已租赁'
            pass
        else:
            from api.v1.views.arkstore import get_arkstore_list
            resp = get_arkstore_list(request, None, 'extension', rented=True, all=True)['items']
            extensions_rented = {ext['package']: ext for ext in resp}
            for ext in items:
                if ext["package"] in extensions_rented:
                    ext["lease_useful_life"] = extensions_rented[ext.package]['lease_useful_life']
                    ext["lease_state"] = '已租赁'

        return {
            'items': items,
            'count': count,
            "previous": f"{request.path}?page={page-1}&page_size={page_size}" if page >= 2 else "",
            "next": f"{request.path}?page={page+1}&page_size={page_size}" if page * page_size < count else ""
        }


class ArstoreAppPagination(CustomPagination):
    def paginate_queryset(self, queryset, pagination: CustomPagination.Input, request, **params):

        if isinstance(queryset,dict) and "error" in queryset.keys() and queryset.get("error") not in ["0",0]:
            queryset["items"] = []
            return queryset

        page = pagination.page
        page_size = pagination.page_size
        items = queryset["items"]
        count = queryset["count"]

        from arkid.core.models import App, PrivateApp
        tenant = request.tenant

        installed_private_apps = PrivateApp.active_objects.filter(tenant=tenant, arkstore_app_id__isnull=False)
        installed_private_apps_dict = {str(app.arkstore_app_id): app for app in installed_private_apps}
        
        installed_apps = App.active_objects.filter(tenant=tenant, arkstore_app_id__isnull=False)
        installed_apps_dict = {str(app.arkstore_app_id): app for app in installed_apps}

        for app in items:
            app['arkstore_uuid'] = app['uuid']
            if app['uuid'] in installed_apps_dict:
                local_app = installed_apps_dict[app['uuid']]
                app['local_uuid'] = str(local_app.id)
                app['installed'] = True
            elif app['uuid'] in installed_private_apps_dict:
                app['installed'] = True
                app['private_app_status'] = installed_private_apps_dict[app['uuid']].status

        return {
            'items': items,
            'count': count,
            "previous": f"{request.path}?page={page-1}&page_size={page_size}" if page >= 2 else "",
            "next": f"{request.path}?page={page+1}&page_size={page_size}" if page * page_size < count else ""
        }