"""
自定义规则校验集合
"""
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

PASSWORD_COMPLEXITY = getattr(settings, "PASSWORD_COMPLEXITY", None)


# pylint: disable=useless-object-inheritance
# pylint: disable=too-many-branches
class _ComplexityValidator(object):
    """自定义密码强度校验规则"""
    message = _("必须更加复杂 (%s)")
    code = "password_complexity"

    def __init__(self, complexities):
        self.complexities = complexities

    def __call__(self, value):
        if self.complexities is None:
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

        if len(uppercase) < self.complexities.get("UPPER", 0):
            errors.append(_("%(UPPER)s 个及以上不同的大写字母") % self.complexities)
        if len(lowercase) < self.complexities.get("LOWER", 0):
            errors.append(_("%(LOWER)s 个及以上不同的小写字母") % self.complexities)
        if len(letters) < self.complexities.get("LETTERS", 0):
            errors.append(_("%(LETTERS)s 个及以上不同的大小写字母") % self.complexities)
        if len(digits) < self.complexities.get("DIGITS", 0):
            errors.append(_("%(DIGITS)s 个及以上不同的数字") % self.complexities)
        if len(special) < self.complexities.get("SPECIAL", 0):
            errors.append(_("%(SPECIAL)s 个及以上的特殊字符") % self.complexities)
        if len(words) < self.complexities.get("WORDS", 0):
            errors.append(_("%(WORDS)s 个及以上不同的单词") % self.complexities)

        if errors:
            raise ValidationError(self.message % (_(u'必须包含 ') + u', '.join(errors), ), code=self.code)


_complexity = _ComplexityValidator(PASSWORD_COMPLEXITY)


# pylint: disable=missing-function-docstring
class ComplexityValidator(object):
    """
    Wrapper for validators.ComplexityValidator which is compatible
    with the Django 1.9+ password validation API
    """
    def __init__(self):
        self.validator = _complexity

    # pylint: disable=no-self-use
    def get_help_text(self):
        return _("密码需满足ArkID的复杂性要求.")

    # pylint: disable=unused-argument
    def validate(self, value, user=None):
        return self.validator(value)
