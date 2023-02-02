import json
import uuid
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.schema import ResponseSchema
from arkid.core.api import GlobalAuth, operation
from arkid.core.models import ExpiringToken, Tenant, User
from arkid.core import pages, actions
from arkid.extension.models import TenantExtensionConfig
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema
from enum import Enum
from pathlib import Path
from django.http import HttpResponse, Http404, JsonResponse
from arkid.core.token import refresh_token
from arkid.core.models import Tenant, User
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.constants import *
from arkid.core.event import BEFORE_REFRESH_TOKEN
from arkid.common.logger import logger
from arkid.core.schema import ResponseSchema
from .models import UserQRCode
from .error import ScanErrorCode
from .schema import QRCodeIn, QRCodeCreateOut, QRCodeStatusOut
from django.utils import timezone
from datetime import datetime, timedelta

ScanAuthFactorSchema = create_extension_schema(
    "ScanAuthFactorSchema",
    __file__,
    [
        (
            'register_enabled',
            bool,
            Field(
                default=False,
                title=_('register_enabled', '启用注册'),
                readonly=True,
                hidden=True,
            ),
        ),
        (
            "reset_password_enabled",
            bool,
            Field(
                default=False,
                title=_("reset_password_enabled", "启用重置密码"),
                readonly=True,
                hidden=True,
            ),
        ),
    ],
    BaseAuthFactorSchema,
)


class ScanAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        self.register_auth_factor_schema(ScanAuthFactorSchema, "Scan")
        self.qrcode_create_path = self.register_api(
            "/qrcode/create",
            "GET",
            self.qrcode_create,
            auth=None,
            response={200: QRCodeCreateOut},
        )
        self.qrcode_status_path = self.register_api(
            "/qrcode/status",
            "GET",
            self.qrcode_status,
            auth=None,
            response={200: QRCodeStatusOut, 404: ResponseSchema},
        )
        self.qrcode_scanned_path = self.register_api(
            "/qrcode/scanned",
            "POST",
            self.qrcode_scanned,
            response={200: ResponseSchema, 404: ResponseSchema},
        )
        self.qrcode_confirmed_path = self.register_api(
            "/qrcode/confirmed",
            "POST",
            self.qrcode_confirmed,
            response={200: ResponseSchema, 404: ResponseSchema},
        )
        self.qrcode_canceled_path = self.register_api(
            "/qrcode/canceled",
            "POST",
            self.qrcode_canceled,
            response={200: ResponseSchema, 404: ResponseSchema},
        )

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def qrcode_create(self, request):
        """
        Generate QR Code
        """
        session_key = request.session.session_key
        qrcode_id = uuid.uuid4().hex
        expired_at = timezone.now() + timedelta(seconds=120)
        UserQRCode.valid_objects.create(
            session_key=session_key, qrcode_id=qrcode_id, expired_at=expired_at
        )

        return JsonResponse({"qrcode_id": qrcode_id})

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def qrcode_status(self, request, qrcode_id: str):
        """
        Check QR Code Status
        """
        session_key = request.session.session_key
        user_qrcode = UserQRCode.valid_objects.filter(
            qrcode_id=qrcode_id, session_key=session_key
        ).first()

        if not user_qrcode:
            return 404, JsonResponse(
                {
                    "error": ScanErrorCode.QRCODE_ID_NOT_FOUND_ERROR.value[0],
                    "message": f"没有找到QRCode ID: {qrcode_id}",
                }
            )
        now = timezone.now()
        is_expired = now > user_qrcode.expired_at

        if user_qrcode.user:
            username = user_qrcode.user.username
            avatar = user_qrcode.user.avatar
            userinfo = {"username": username, "avatar": avatar}
        else:
            userinfo = None

        if user_qrcode.status == "confirmed":
            exp_token = ExpiringToken.objects.filter(user=user_qrcode.user).first()
            token = exp_token.token
            return JsonResponse(
                {
                    "qrcode_id": qrcode_id,
                    "expired": is_expired,
                    "status": user_qrcode.status,
                    "userinfo": userinfo,
                    "token": token,
                }
            )

        return JsonResponse(
            {
                "qrcode_id": qrcode_id,
                "expired": is_expired,
                "status": user_qrcode.status,
                "userinfo": userinfo,
            }
        )

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def qrcode_scanned(self, request, data: QRCodeIn):
        """
        Generate QR Code
        """
        user = request.user
        qrcode_id = data.qrcode_id
        user_qrcode = UserQRCode.valid_objects.filter(qrcode_id=qrcode_id).first()

        if not user_qrcode:
            return 404, self.error(ScanErrorCode.QRCODE_ID_NOT_FOUND_ERROR)
        user_qrcode.status = "scanned"
        user_qrcode.user = user
        user_qrcode.save()

        return JsonResponse({"error": ErrorCode.OK.value, "message": "扫码成功"})

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def qrcode_confirmed(self, request, data: QRCodeIn):
        """
        Generate QR Code
        """
        qrcode_id = data.qrcode_id
        user_qrcode = UserQRCode.valid_objects.filter(qrcode_id=qrcode_id).first()

        if not user_qrcode:
            return self.error(ScanErrorCode.QRCODE_ID_NOT_FOUND_ERROR)
        now = timezone.now()
        is_expired = now > user_qrcode.expired_at
        if is_expired:
            return self.error(ScanErrorCode.QRCODE_ID_EXPIRED_ERROR)
        user_qrcode.status = "confirmed"
        user_qrcode.save()

        return JsonResponse({"error": ErrorCode.OK.value, "message": "确认成功"})

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def qrcode_canceled(self, request, data: QRCodeIn):
        """
        Generate QR Code
        """
        qrcode_id = data.qrcode_id
        user_qrcode = UserQRCode.valid_objects.filter(qrcode_id=qrcode_id).first()

        if not user_qrcode:
            return self.error(ScanErrorCode.QRCODE_ID_NOT_FOUND_ERROR)
        user_qrcode.status = "canceled"
        user_qrcode.save()

        return JsonResponse({"error": ErrorCode.OK.value, "message": "取消成功"})

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

        config_data[self.LOGIN]["forms"].append(
            {
                "label": "扫码登录",
                "items": [
                    {
                        "name": "qrcode_login",
                        "type": "qrcode",
                        "qrcode_get_url": self.qrcode_create_path,
                        "qrcode_check_url": self.qrcode_status_path,
                    }
                ],
                "scripts": [],
            }
        )

    def create_register_page(self, event, config, config_data):
        pass

    def create_password_page(self, event, config, config_data):
        pass

    def create_other_page(self, event, config, config_data):
        pass

    def create_auth_manage_page(self):

        name = '扫码登录'

        page = pages.ScanPage(name=name)
        return page


extension = ScanAuthFactorExtension()
