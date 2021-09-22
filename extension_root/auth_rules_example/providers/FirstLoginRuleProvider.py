
from django.urls.base import reverse
from login_register_config.models import LoginRegisterConfig
from typing import Dict
from common.provider import BaseAuthRuleProvider
from runtime import get_app_runtime
from common import loginpage as login_page_model

class FirstLoginRuleProvider(BaseAuthRuleProvider):

    def create(self, auth_rule, data) -> Dict:
        return data

    def delete(self):
        return super().delete()

    def update(self):
        return super().update()

    def run(self, *args, **kwargs):
        return

    def change_form(self, auth_rule, request, form, tenant):
        print(request, form, tenant)
        return

    def authenticate_failed(self, auth_rule, request, form, tenant):
        extension = request.data.get("extension", None)

        if extension in auth_rule.data["major_auth"]:
            login_fail_count = request.session.get(
                f"{extension}_fail_count", 0)
            print(login_fail_count)
            if login_fail_count >= auth_rule.data.get("times",3):
                # 更换登录页面为次认证因素页面
                auth_factors = auth_rule.data["second_auth"]
                for auth_factor in auth_factors:
                    config = LoginRegisterConfig.active_objects.filter(tenant=tenant,type=auth_factor).first()
                    if not config:
                        config_data = {

                        }
                    else:
                        config_data = config.data

                    url = reverse('api:login')
                    if tenant:
                        url += '?tenant=tenant_uuid'

                    auth_provider = get_app_runtime().login_register_config_providers.get(auth_factor,None)(data=config_data)
                    if auth_provider:
                        form["command"] = "refresh_page"

                        login_form = auth_provider.login_form
                        items = login_form.get('items')
                        items.append(
                            login_page_model.LoginFormItem(type='hidden', name='extension', value=auth_factor)
                        )

                        form['submit'] = login_page_model.Button(
                            label='登录', http=login_page_model.ButtonHttp(url=url, method='post')
                        )

                        if form.get("form_data",None):
                            form["form_data"].extend(login_form)
                        else:
                            form["form_data"] = [login_form]

                    
            else:
                request.session[f"{extension}_fail_count"] = login_fail_count+1

        return super().authenticate_failed(auth_rule, request, form, tenant)

    def authenticate_success(self, auth_rule, request, form, user, tenant):
        extension = request.data.get("extension", None)
        request.session[f"{extension}_fail_count"] = 0
        return super().authenticate_success(auth_rule, request, form, user, tenant)
