from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from extension_root.tenantuserconfig.models import TenantUserConfig
from inventory.models import User


class ChildUserSerializer(BaseDynamicFieldModelSerializer):

    username = serializers.CharField(label=_('账户名'))
    account_type = serializers.CharField(label=_('类型'), read_only=True)
    email = serializers.CharField(label=_('邮箱'))
    mobile = serializers.CharField(label=_('手机'))
    password = serializers.CharField(label=_('密码'), write_only=True, required=False)

    class Meta:
        model = User

        fields = (
            'uuid',
            'username',
            'account_type',
            'password',
            'email',
            'mobile',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    def create(self, validated_data):
        request = self.context['request']
        parent = request.user
        username = validated_data.get('username')
        email = validated_data.get('email')
        mobile = validated_data.get('mobile')
        password = validated_data.get('password')

        user = User()
        user.username = username
        user.email = email
        user.mobile = mobile
        user.parent = parent
        user.save()
        for tenant in parent.tenants.all():
            user.tenants.add(tenant)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.__dict__.update(validated_data)
        instance.save()
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class ChildUserCheckTypeSerializer(serializers.Serializer):
    is_success = serializers.BooleanField(label=_('是否成功切换'))


class ChildUserGetTokenSerializer(serializers.Serializer):
    token = serializers.CharField(label=_('token'))