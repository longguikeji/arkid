from oneid_meta.models import User, AccountConfig
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, label=_("Username"))
    private_email = serializers.CharField(required=False)
    mobile = serializers.CharField(required=False)

    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        user = None
        username = attrs.get('username', '')
        private_email = attrs.get('private_email', '')
        mobile = attrs.get('mobile', '')
        password = attrs.get('password')

        if not password:
            msg = _('Must include "password".')
            raise serializers.ValidationError(msg, code='authorization')

        if not (username or mobile or password):
            msg = _('Must include "username" or "private_email" or "mobile".')
            raise serializers.ValidationError(msg, code='authorization')

        msg = _('Unable to log in with provided credentials.')
        if username:
            user = User.valid_objects.filter(username=username).first()
            if not user or not user.check_password(password):
                raise serializers.ValidationError(msg, code='authorization')

        account_config = AccountConfig.get_current()

        if private_email:
            if not account_config.support_email:
                raise serializers.ValidationError({'private_email': ['unsupport']})
            user = User.valid_objects.filter(private_email=private_email).first()
            if not user or not user.check_password(password):
                raise serializers.ValidationError(msg, code='authorization')

        if mobile:
            if not account_config.support_mobile:
                raise serializers.ValidationError({'mobile': ['unsupport']})
            user = User.valid_objects.filter(mobile=mobile).first()
            if not user or not user.check_password(password):
                raise serializers.ValidationError(msg, code='authorization')

        if user is None:
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
