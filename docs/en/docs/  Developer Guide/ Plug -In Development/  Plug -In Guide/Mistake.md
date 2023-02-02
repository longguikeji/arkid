# mistake

APIWhen the interface needs to be returned error，Call [seld.error](../%20 plug -in base class/#arkid.core.extension.Extension.ERROR) method

Plug -in developers need to write their own error uniformly.py file，Error codes and error messages that use enumeration parameters packaging plugins
Unity in a place that needs to be returned，Call [seld.error](../%20 plug -in base class/#arkid.core.extension.Extension.Error) The specific enumeration object that needs to be prompted in，This method returns to the encapsulated error message dictionary

``` py title="error.py"

from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USERNAME_PASSWORD_MISMATCH = ('10001-1', _('username or password not correct', 'wrong user name or password'))
    CONTACT_MANAGER = ('10001-5', _('contact manager', 'Accident，Please contact the manager'))
    USERNAME_EMPTY = ('10001-6', _('username empty', 'User name is empty'))
    ALL_USER_FLAG_LACK_FIELD = ('10001-7', _('fill in at least one user ID', 'All user logos fill in at least one'))
    FIELD_USER_EXISTS = ('10001-8', _('fill in at least one user ID', '{field}Fields and already some users repeat'))
    PASSWORD_STRENGTH_LACK = ('10001-9', _('password strength lack', ' Insufficient password strength'))
    TWO_TIME_PASSWORD_MISMATCH = ('10001-10', _('two time password mismatch', 'Different passwords input differently'))
    OLD_PASSWORD_ERROR = ('10001-10', _('old password error', 'The old password does not match'))

```

``` py

....
    return self.error(ErrorCode.USERNAME_PASSWORD_MISMATCH)
....
```

If normal return value，Call [self.success](../%20 plug -in base class/#arkid.core.extension.Extension.success) Come back

``` py

....
    def api_function(self.request):
        ....
        return self.success({'key':value})
....

```
