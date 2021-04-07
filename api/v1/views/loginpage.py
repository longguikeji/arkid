from rest_framework import views
from ..serializers import loginpage as lp
from common import loginpage as model
from openapi.utils import extend_schema
from django.http.response import JsonResponse
from api.v1.views.login import LoginView, MobileLoginView
from api.v1.views.tenant import TenantViewSet
from runtime import get_app_runtime
from tenant.models import Tenant

@extend_schema(tags = ['login page'])
class LoginPage(views.APIView):

    @extend_schema(
        responses=lp.LoginPagesSerializer
    )
    def get(self, request):
        tenant_uuid = request.query_params.get('tenant', None)
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        data = model.LoginPages()
        if tenant:
            data.addForm( model.LOGIN, TenantViewSet().login_form(tenant.id) )
            data.addForm( model.LOGIN, TenantViewSet().mobile_login_form(tenant.id) )
            data.addForm( model.REGISTER, TenantViewSet().mobile_register_form(tenant.id) )
        else:
            data.addForm( model.LOGIN, LoginView().login_form() )
            data.addForm( model.LOGIN, MobileLoginView().login_form() )
        
        if data.getPage(model.REGISTER):
            data.addBottom(model.LOGIN, model.Button(
                prepend='还没有账号，',
                label='立即注册',
                gopage=model.REGISTER
            ))
            data.addBottom(model.REGISTER, model.Button(
                prepend='已有账号，',
                label='立即登录',
                gopage=model.LOGIN
            ))
        
        if data.getPage(model.PASSWORD):
            data.addBottom(model.LOGIN, model.Button(
                label='忘记密码',
                gopage='password'
            ))
        
        
        
        pages = lp.LoginPagesSerializer(data=data)
        pages.is_valid()
        return JsonResponse(pages.data)