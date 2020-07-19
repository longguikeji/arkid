"""
自定义密码复杂度校验
"""
import re

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from oneid_meta.models import PasswordComplexityConfig


# pylint: disable=useless-object-inheritance
# pylint: disable=too-many-branches
class _ComplexityValidator(object):
    """自定义密码复杂度校验规则"""
    message = _("密码必须更加复杂 (%s)")
    code = "password_complexity"

    def __init__(self):
        self.pwd_config = PasswordComplexityConfig.get_current()

    def __call__(self, value):
        self.__init__()
        # 未开启密码复杂度校验
        if not self.pwd_config.is_active:
            return
        uppercase, lowercase, letters, digits, special = set(), set(), set(), set(), set()
        errors = []

        for _character in value:
            if _character.isupper():
                uppercase.add(_character)
                letters.add(_character)
                continue
            if _character.islower():
                lowercase.add(_character)
                letters.add(_character)
                continue
            if _character.isdigit():
                digits.add(_character)
                continue
            if not _character.isspace():
                special.add(_character)

        words = set(re.findall(r'\b\w+', value, re.UNICODE))

        if len(uppercase) < self.pwd_config.min_upper:
            errors.append(_(f"{self.pwd_config.min_upper} 个及以上不同的大写字母").__str__())

        if len(lowercase) < self.pwd_config.min_lower:
            errors.append(_(f"{self.pwd_config.min_lower} 个及以上不同的小写字母").__str__())

        if len(letters) < self.pwd_config.min_letter:
            errors.append(_(f"{self.pwd_config.min_letter} 个及以上不同的大小写字母").__str__())

        if len(digits) < self.pwd_config.min_digit:
            errors.append(_(f"{self.pwd_config.min_digit} 个及以上不同的数字").__str__())

        if len(special) < self.pwd_config.min_special:
            errors.append(_(f"{self.pwd_config.min_special} 个及以上的特殊字符").__str__())

        if len(words) < self.pwd_config.min_word:
            errors.append(_(f"{self.pwd_config.min_word} 个及以上不同的单词").__str__())

        if len(value) < self.pwd_config.min_length:
            errors.append(_(f"{self.pwd_config.min_length} 长度及以上的密码").__str__())

        if errors:
            raise ValidationError(self.message % (_(u'必须包含 ') + u', '.join(errors), ), code=self.code)


# _COMPLEXITY = _ComplexityValidator(PasswordComplexityConfig.get_current())


# pylint: disable=missing-function-docstring
class ComplexityValidator:
    """
    Wrapper for validators.ComplexityValidator which is compatible
    with the Django 1.9+ password validation API
    """
    def __init__(self):
        self.validator = _ComplexityValidator()

    # pylint: disable=no-self-use
    def get_help_text(self):
        return _("密码需满足ArkID的复杂性要求.")

    # pylint: disable=unused-argument
    def validate(self, value, user=None):
        return self.validator(value)
