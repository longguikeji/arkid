"""
serializer for aliyun Role SSO
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import AliyunSSORole, User


class AliyunSSORoleSerializer(DynamicFieldsModelSerializer):
    """Serializer for Aliyun SSO Role"""

    user_id = serializers.IntegerField(source='user.id', required=True)
    role = serializers.ListField(required=False, child=serializers.CharField(allow_blank=False))
    session_duration = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:    # pylint: disable=missing-docstring
        model = AliyunSSORole

        fields = ('user_id', 'role', 'session_duration', 'is_active')

    def create(self, validated_data):
        """create sso role"""
        user_id = validated_data.pop('user')['id']
        user = User.valid_objects.filter(id=user_id).first()
        role = AliyunSSORole.objects.create(user=user, **validated_data)
        return role

    def update(self, instance, validated_data):    # pylint: disable=too-many-statements,too-many-branches
        """update sso role"""
        role = instance

        user_id = validated_data.pop('user')['id']
        if user_id and user_id != role.user.id:
            raise ValidationError({'user_id': ['this field is immutable']})

        role.__dict__.update(validated_data)
        role.save()
        return role

    def validate_user_id(self, value):
        """
        校验user是否已经配置阿里云角色SSO信息
        """
        if not User.valid_objects.filter(id=value).exists():
            raise ValidationError(['user not existed'])
        exclude = {'pk': self.instance.pk} if self.instance else {}
        if self.Meta.model.valid_objects.filter(user__id=value).exclude(**exclude).exists():
            raise ValidationError(['aliyun sso role existed'])
        return value
