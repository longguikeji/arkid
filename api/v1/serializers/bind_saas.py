from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class ArkIDBindSaasSerializer(serializers.Serializer):

    company_name = serializers.CharField(label=_('公司名'), read_only=False)
    contact_person = serializers.CharField(label=_('联系人'), read_only=False)
    email = serializers.CharField(label=_('邮箱'), read_only=False)
    mobile = serializers.CharField(label=_('手机'), read_only=False)
    local_tenant_slug = serializers.CharField(label=_('本地租户Slug'), read_only=True)
    local_tenant_uuid = serializers.CharField(label=_('本地租户UUID'), read_only=True)
    saas_tenant_slug = serializers.CharField(label=_('中心平台租户Slug'), read_only=False)
    saas_tenant_uuid = serializers.CharField(label=_('中心平台租户UUID'), read_only=True)
    saas_tenant_url = serializers.CharField(label=_('中心平台网址'), read_only=True)


class ArkIDBindSaasCreateSerializer(serializers.Serializer):

    slug = serializers.SlugField(label=_('中心租户Slug'), read_only=False)
    company_name = serializers.CharField(label=_('公司名'), read_only=False)
    contact_person = serializers.CharField(label=_('联系人'), read_only=False)
    email = serializers.EmailField(label=_('邮箱'), read_only=False)
    mobile = serializers.CharField(label=_('手机'), read_only=False)
