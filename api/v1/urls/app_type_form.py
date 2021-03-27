from api.v1.views import (
    app_type_form as views_app_type_form
)

from .tenant import tenant_router


tenant_app_type_form_router = tenant_router.register(r'app_type_form', views_app_type_form.AppTypeFormViewSet, basename='tenant-app-type-form', parents_query_lookups=['tenant'])
