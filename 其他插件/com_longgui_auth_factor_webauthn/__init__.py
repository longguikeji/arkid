import json
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.schema import ResponseSchema
from arkid.core.constants import *
from arkid.core.api import GlobalAuth, operation
from .error import WebauthnErrorCode
from arkid.core.models import Tenant, User
from arkid.core import pages, actions
from arkid.extension.models import TenantExtensionConfig
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema
from api.v1.pages.user_manage.user_list import page as user_list_page
from enum import Enum
from pathlib import Path
from django.http import HttpResponse, Http404, JsonResponse
from .schema import (
    RegistrationOptionsRequestSchema,
    RegistrationResponseSchema,
    AuthenticationOptionsRequestSchema,
    AuthenticationResponseSchema,
    ListMineCredentialsOut,
    CredentialItemSchema,
    WebAuthnCredential,
)
from .services import (
    RegistrationService,
    CredentialService,
    AuthenticationService,
    SessionService,
)
from webauthn import options_to_json
from arkid.core.token import refresh_token
from arkid.core.models import Tenant, User
from arkid.core.error import ErrorCode, ErrorDict
from .helpers import transports_to_ui_string, truncate_credential_id_to_ui_string
from .models import UserWebauthnCredential


class Attestation(str, Enum):
    none = _("none", "none")
    direct = _("direct", "direct")


class Attachment(str, Enum):
    none = _("all", "all")
    cross_platform = _("cross_platform", "cross_platform")
    platform = _("platform", "platform")


WebauthnAuthFactorSchema = create_extension_schema(
    "WebauthnAuthFactorSchema",
    __file__,
    [
        (
            "require_user_verification",
            Optional[bool],
            Field(default=True, title=_("require_user_verification", "需要用户认证")),
        ),
        (
            "alg_es256",
            Optional[bool],
            Field(default=True, title=_("es256 support", "支持ES256算法")),
        ),
        (
            "alg_rs256",
            Optional[bool],
            Field(default=True, title=_("rs256 support", "支持RS256算法")),
        ),
        ("attestation", Attestation, Field(title=_("Attestation", "验证认证器方式"))),
        (
            "attachment",
            Attachment,
            Field(title=_("Authenticator Attachment", "认证器类型")),
        ),
        (
            "RP_ID",
            str,
            Field(default='localhost', title=_("RP_ID", "依赖方ID(当前域名或子域名)")),
        ),
        (
            "RP_NAME",
            str,
            Field(default='ArkID', title=_("RP_NAME", "依赖方名称(方便用户识别)")),
        ),
        (
            "RP_EXPECTED_ORIGIN",
            str,
            Field(
                default='http://localhost:9528', title=_("RP_EXPECTED_ORIGIN", "当前域名")
            ),
        ),
        (
            "reset_password_enabled",
            bool,
            Field(
                default=False, title=_("reset_password_enabled", "启用重置密码"), hidden=True
            ),
        ),
    ],
    BaseAuthFactorSchema,
)


class WebauthnAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        # self.register_extend_field(UserPassword, "password")
        self.register_auth_factor_schema(WebauthnAuthFactorSchema, "webauthn")
        self.register_api("/js/{filename}", "GET", self.serve_js_file, auth=None)
        self.register_api(
            "/registration/options", "POST", self.registration_options, auth=None
        )
        self.register_api(
            "/registration/verification",
            "POST",
            self.registration_verification,
            auth=None,
        )
        self.register_api(
            "/registration/inner_verification",
            "POST",
            self.registration_inner_verification,
        )
        self.register_api(
            "/authentication/options", "POST", self.authentication_options, auth=None
        )
        self.register_api(
            "/authentication/verification",
            "POST",
            self.authentication_verification,
            auth=None,
        )
        self.register_api(
            "/registration/inner_info",
            "GET",
            self.inner_registration_info,
            tenant_path=True,
        )

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def inner_registration_info(self, request, tenant_id: str):
        """
        Generate info for a WebAuthn registration inside arkid
        """

        tenant = request.tenant
        user = request.user

        configs = self.get_tenant_configs(tenant=tenant)
        if not configs:
            config_id = ''
        else:
            config_id = configs[0].id.hex
        return JsonResponse({"username": user.username, "config_id": config_id})

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def registration_options(
        self, request, form_data: RegistrationOptionsRequestSchema
    ):
        """
        Generate options for a WebAuthn registration ceremony
        """

        options_username = form_data.username
        config_id = form_data.config_id
        config = self.get_config_by_id(config_id)

        options_attestation = config.config.get("attestation")
        options_attachment = config.config.get("attachment")
        options_require_user_verification = config.config.get(
            "require_user_verification"
        )
        alg_es256 = config.config.get("alg_es256")
        alg_rs256 = config.config.get("alg_rs256")

        options_algorithms = []
        if alg_es256:
            options_algorithms.append("es256")

        if alg_rs256:
            options_algorithms.append("rs256")

        registration_service = RegistrationService()
        credential_service = CredentialService()

        registration_options = registration_service.generate_registration_options(
            config=config,
            username=options_username,
            attachment=options_attachment,
            attestation=options_attestation,
            algorithms=options_algorithms,
            require_user_verification=options_require_user_verification,
            existing_credentials=credential_service.retrieve_credentials_by_username(
                username=options_username
            ),
        )

        options_json = json.loads(options_to_json(registration_options))

        # Add in credProps extension
        options_json["extensions"] = {
            "credProps": True,
        }

        return JsonResponse(options_json)

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def registration_verification(self, request, form_data: RegistrationResponseSchema):
        """
        Verify the response from a WebAuthn registration ceremony
        """
        # form_data = json.loads(data)
        username: str = form_data.username
        webauthn_response: dict = form_data.response
        config_id = form_data.config_id
        config = self.get_config_by_id(config_id)

        user = User.active_objects.filter(username=username).first()
        if user:
            return self.error(ErrorCode.USERNAME_EXISTS_ERROR)
        registration_service = RegistrationService()

        try:
            verification = registration_service.verify_registration_response(
                config=config,
                username=username,
                response=webauthn_response,
            )

            transports: list = webauthn_response.get("transports", [])
            extensions: dict = webauthn_response.get("clientExtensionResults", {})
            ext_cred_props: dict = extensions.get("credProps", {})
            is_discoverable_credential: bool = ext_cred_props.get("rk", False)

        except Exception as err:
            return JsonResponse(
                {
                    "error": WebauthnErrorCode.REGISTRATION_VERIFICATION_ERROR.value,
                    "message": str(err),
                },
                status=400,
            )

        # 生成 token
        user = User(tenant=config.tenant)
        user.username = username
        user.save()

        # Store credential for later
        credential_service = CredentialService()
        credential_service.store_credential(
            user=user,
            username=username,
            verification=verification,
            transports=transports,
            is_discoverable_credential=is_discoverable_credential,
        )

        token = refresh_token(user)

        # return JsonResponse({"verified": True})
        return JsonResponse(
            {
                "error": ErrorCode.OK.value,
                "data": {
                    "user": {"id": user.id.hex, "username": user.username},
                    "token": token,
                },
            }
        )

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def registration_inner_verification(
        self, request, form_data: RegistrationResponseSchema
    ):
        """
        Verify the response from a WebAuthn registration ceremony
        """
        # form_data = json.loads(data)
        user = request.user
        username: str = form_data.username
        webauthn_response: dict = form_data.response
        config_id = form_data.config_id
        config = self.get_config_by_id(config_id)

        # user = User.active_objects.filter(username=username).first()
        # if user:
        #     return self.error(ErrorCode.USERNAME_EXISTS_ERROR)
        registration_service = RegistrationService()

        try:
            verification = registration_service.verify_registration_response(
                config=config,
                username=username,
                response=webauthn_response,
            )

            transports: list = webauthn_response.get("transports", [])
            extensions: dict = webauthn_response.get("clientExtensionResults", {})
            ext_cred_props: dict = extensions.get("credProps", {})
            is_discoverable_credential: bool = ext_cred_props.get("rk", False)

        except Exception as err:
            return JsonResponse(
                {
                    "error": WebauthnErrorCode.REGISTRATION_VERIFICATION_ERROR.value,
                    "message": str(err),
                },
                status=400,
            )

        # # 生成 token
        # user = User(tenant=config.tenant)
        # user.username = username
        # user.save()

        # Store credential for later
        credential_service = CredentialService()
        credential_service.store_credential(
            user=user,
            username=username,
            verification=verification,
            transports=transports,
            is_discoverable_credential=is_discoverable_credential,
        )

        # token = refresh_token(user)

        # return JsonResponse({"verified": True})
        return JsonResponse(
            {
                "error": ErrorCode.OK.value,
                "data": {
                    "user": {"id": user.id.hex, "username": user.username},
                    # "token": token,
                },
            }
        )

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def authentication_options(
        self, request, form_data: AuthenticationOptionsRequestSchema
    ):

        options_username = form_data.username
        config_id = form_data.config_id
        config = self.get_config_by_id(config_id)

        options_require_user_verification = config.config.get(
            "require_user_verification"
        )

        authentication_service = AuthenticationService()
        session_service = SessionService()

        existing_credentials = []
        if options_username:
            credential_service = CredentialService()
            existing_credentials = credential_service.retrieve_credentials_by_username(
                username=options_username
            )

            if len(existing_credentials) == 0:
                return JsonResponse(
                    self.error(WebauthnErrorCode.AUTHENTICATION_NO_CREDENTIAL_ERROR),
                    status=400,
                )

        authentication_options = authentication_service.generate_authentication_options(
            config=config,
            cache_key=session_service.get_session_key(request=request),
            require_user_verification=options_require_user_verification,
            existing_credentials=existing_credentials,
        )

        return JsonResponse(json.loads(options_to_json(authentication_options)))

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def authentication_verification(
        self, request, form_data: AuthenticationResponseSchema
    ):
        """
        Verify the response from a WebAuthn authentication ceremony
        """
        options_username = form_data.username
        options_webauthn_response: dict = form_data.response
        config_id = form_data.config_id
        config = self.get_config_by_id(config_id)

        authentication_service = AuthenticationService()
        credential_service = CredentialService()
        session_service = SessionService()

        try:
            existing_credential = credential_service.retrieve_credential_by_id(
                credential_id=options_webauthn_response["id"],
                username=options_username,
            )

            verification = authentication_service.verify_authentication_response(
                config=config,
                cache_key=session_service.get_session_key(request=request),
                existing_credential=existing_credential,
                response=options_webauthn_response,
            )

            # Update credential with new sign count
            credential_service.update_credential_sign_count(verification=verification)
        except Exception as err:
            return JsonResponse(
                {
                    "error": WebauthnErrorCode.AUTHENTICATION_VERIFICATION_ERROR.value,
                    "message": str(err),
                },
                status=400,
            )

        # session_service.log_in_user(request=request, username=verification.username)
        user = User.active_objects.filter(username=verification.username).first()
        if not user:
            return JsonResponse(
                {
                    "error": WebauthnErrorCode.AUTHENTICATION_VERIFICATION_ERROR.value,
                    "message": '用户不存在, 或许已被删除',
                },
                status=400,
            )

        token = refresh_token(user)

        return JsonResponse(
            {
                "error": ErrorCode.OK.value,
                "data": {
                    "user": {"id": user.id.hex, "username": user.username},
                    "token": token,
                },
            }
        )

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def serve_js_file(self, request, filename: str):
        BASE_DIR = Path(__file__).resolve().parent
        file_path = BASE_DIR.joinpath("static", filename)
        if not file_path.is_file():
            raise Http404
        js_file = open(file_path, "rb")
        response = HttpResponse(content=js_file)
        response["Content-Type"] = "text/javascript"
        return response

    def check_auth_data(self, event, **kwargs):
        pass

    def fix_login_page(self, event, **kwargs):
        pass

    def authenticate(self, event, **kwargs):
        pass

    @transaction.atomic()
    def register(self, event, **kwargs):
        pass

    def reset_password(self, event, **kwargs):
        pass

    def create_login_page(self, event, config, config_data):
        items = [
            {"type": "text", "name": "username", "placeholder": "用户名"},
        ]
        items.append({"type": "hidden", "name": "config_id", "value": config.id})
        # self.add_page_form(config, self.LOGIN, "用户名密码登录", items, config_data)
        config_data[self.LOGIN]["forms"].append(
            {
                "label": "Webauthn",
                "items": items,
                "submit": {
                    "label": "登录",
                    "title": "登录",
                    "action": "webauthnStartAuthentication",
                },
                "scripts": [
                    {
                        "src": "/api/v1/com_longgui_auth_factor_webauthn/js/simplewebauthn-browser.6.2.1.umd.min.js"
                    },
                    {
                        "src": "/api/v1/com_longgui_auth_factor_webauthn/js/webauthn-form.js",
                        "globals": [
                            "webauthnStartAuthentication",
                            "webauthnStartRegistration",
                        ],
                    },
                ],
            }
        )

    def create_register_page(self, event, config, config_data):
        items = [
            {"type": "text", "name": "username", "placeholder": "用户名"},
        ]
        items.append({"type": "hidden", "name": "config_id", "value": config.id})
        # self.add_page_form(config, self.LOGIN, "用户名密码登录", items, config_data)
        config_data[self.REGISTER]["forms"].append(
            {
                "label": "Webauthn",
                "items": items,
                "submit": {
                    "label": "注册",
                    "title": "注册",
                    "action": "webauthnStartRegistration",
                },
            }
        )

    def create_password_page(self, event, config, config_data):
        pass

    def create_other_page(self, event, config, config_data):
        pass

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def list_mine_credentials(self, request):
        user = request.user
        credentials = user.webauthn_credential_set.all()
        result = []
        for item in credentials:
            cred = WebAuthnCredential.parse_obj(item.credential)
            result.append(
                {
                    "id": item.id.hex,
                    "cred_id": truncate_credential_id_to_ui_string(cred.id),
                    "sign_count": cred.sign_count,
                    "is_disc_cred": cred.is_discoverable_credential,
                    "transports": transports_to_ui_string(cred.transports or []),
                    "device_type": cred.device_type.lower().replace("_", "-"),
                    "backed_up": cred.backed_up,
                }
            )
        return result

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def delete_mine_credential(self, request, tenant_id: str, id: str):
        user = request.user
        user_dict = User.expand_objects.filter(id=user.id).first()
        password = user_dict.get('password')
        all_user_cred = UserWebauthnCredential.active_objects.filter(user=user)

        # 没有设置密码，况且当前只有一个凭证，不能删除
        if not password and len(all_user_cred) == 1:
            return ErrorDict(WebauthnErrorCode.CREDENTIAL_DELETE_ERROR)

        cred = all_user_cred.filter(id=id).first()
        if cred:
            cred.kill()

        return ErrorDict(ErrorCode.OK)

    def create_auth_manage_page(self):
        # Webauthn凭证管理

        list_webauthn_credentials = self.register_api(
            "/mine_webauthn_credentials/",
            'GET',
            self.list_mine_credentials,
            response=List[CredentialItemSchema],
        )
        delete_webauthn_credential = self.register_api(
            "/mine_webauthn_credentials/{id}",
            'DELETE',
            self.delete_mine_credential,
            tenant_path=True,
            # response=ListMineCredentialsOut,
        )

        name = 'Webauthn凭证管理'

        page = pages.TablePage(name=name)
        page.create_actions(
            init_action=actions.DirectAction(
                path=list_webauthn_credentials, method=actions.FrontActionMethod.GET
            ),
            local_actions={
                "unbind": actions.DirectAction(
                    name='删除',
                    path=delete_webauthn_credential,
                    method=actions.FrontActionMethod.DELETE,
                ),
            },
            global_actions={
                'create': actions.ScriptAction(
                    scripts=[
                        {
                            "src": "/api/v1/com_longgui_auth_factor_webauthn/js/simplewebauthn-browser.6.2.1.umd.min.js"
                        },
                        {
                            "src": "/api/v1/com_longgui_auth_factor_webauthn/js/webauthn-form.js",
                            "globals": [
                                "webauthnStartAuthentication",
                                "webauthnStartRegistration",
                            ],
                        },
                    ],
                    script_func="webauthnInnerRegistration",
                    name=_("创建"),
                    icon="icon-create",
                ),
            },
        )
        return page


extension = WebauthnAuthFactorExtension()
