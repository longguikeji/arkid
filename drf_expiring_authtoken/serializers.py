from ..oneid_meta.models import User, AccountConfig
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from ..infrastructure.serializers.sms import (
    LoginSMSClaimSerializer,
)


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, label=_("Username"))
    private_email = serializers.CharField(required=False)
    mobile = serializers.CharField(required=False)

    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'}, trim_whitespace=False, required=False)
    sms_token = serializers.CharField(required=False)

    def validate(self, attrs):
        username = attrs.get('username', '')
        private_email = attrs.get('private_email', '')
        password = attrs.get('password')
        mobile = attrs.get('mobile', '')
        sms_token = attrs.get('sms_token', '')

        def get_user(required_key: str, required_value: str, index_key: str, index_value: str, check_pw: bool) -> User:
            if not required_value:
                _msg = _('Must include "{0}".').format(required_key)
                raise serializers.ValidationError(_msg, code='authorization')
            _user = User.valid_objects.filter(**{index_key: index_value}).first()
            if not _user or (check_pw and not _user.check_password(password)):
                _msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(_msg, code='authorization')
            return _user

        account_config = AccountConfig.get_current()

        if username:
            user = get_user('password', password, 'username', username, check_pw=True)

        elif mobile:
            if not account_config.support_mobile:
                raise serializers.ValidationError({'mobile': ['unsupport']})
            user = get_user('sms_token', sms_token, 'mobile', mobile, check_pw=False)
            if LoginSMSClaimSerializer.check_sms_token(sms_token)['mobile'] != mobile:
                msg = _("Phone and captcha don't match")
                raise serializers.ValidationError(msg, code='authorization')
            LoginSMSClaimSerializer.clear_sms_token(sms_token)

        elif private_email:
            if not account_config.support_email:
                raise serializers.ValidationError({'private_email': ['unsupport']})
            user = get_user('password', password, 'private_email', private_email, check_pw=True)

        else:
            msg = _('Must include "username" or "private_email" or "mobile".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs