from common.provider import PrivacyNoticeProvider
from tenant.models import Tenant
from config.models import PrivacyNotice
from .constants import KEY


class Provider(PrivacyNoticeProvider):
    @classmethod
    def load_privacy(cls, request):
        tenant_uuid = request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()

        privacy_notice = PrivacyNotice.valid_objects.filter(tenant=tenant).first()
        if not privacy_notice:
            privacy_notice = PrivacyNotice.objects.create(tenant=tenant, is_active=True)

        return privacy_notice
