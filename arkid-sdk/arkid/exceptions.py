import logging
import requests

logger = logging.getLogger(__name__)


class ArkIDError(Exception):
    """
    Root of the ArkID Exception hierarchy.
    """


class ArkIDSDKUsageError(ArkIDError, ValueError):
    """
    A ``ArkIDSDKUsageError`` may be thrown in cases in which the SDK
    detects that it is being used improperly.

    These errors typically indicate that some contract regarding SDK usage
    (e.g. required order of operations) has been violated.
    """


class ArkIDAPIError(ArkIDError):
    """
    Wraps errors returned by a REST API.

    :ivar http_status: HTTP status code (int)
    :ivar code: Error code from the API (str),
                or "Error" for unclassified errors
    :ivar message: Error message from the API. In general, this will be more
                   useful to developers, but there may be cases where it's
                   suitable for display to end users.
    """

    def __init__(self, response, *args, **kwargs):
        self._underlying_response = response
        self.http_status = response.status_code
        if "Content-Type" in response.headers and (
            "application/json" in response.headers["Content-Type"]
        ):
            logger.debug(
                (
                    "Content-Type on error is application/json. "
                    "Doing error load from JSON"
                )
            )
            try:
                self._load_from_json(response.json())
            except (KeyError, ValueError):
                logger.error(
                    (
                        "Error body could not be JSON decoded! "
                        "This means the Content-Type is wrong, or the "
                        "body is malformed!"
                    )
                )
                self._load_from_text(response.text)
        else:
            logger.debug(
                (
                    "Content-Type on error is unknown. "
                    "Failing over to error load as text (default)"
                )
            )
            # fallback to using the entire body as the message for all other types
            self._load_from_text(response.text)
        args = self._get_args()
        ArkIDError.__init__(self, *args)

    @property
    def raw_json(self):
        """
        Get the verbatim error message received from a ArkID API, interpreted
        as a JSON string and evaluated as a *dict*

        If the body cannot be loaded as JSON, this is None
        """
        response = self._underlying_response
        if "Content-Type" in response.headers and (
            "application/json" in response.headers["Content-Type"]
        ):
            try:
                return response.json()
            except ValueError:
                logger.error(
                    (
                        "Error body could not be JSON decoded! "
                        "This means the Content-Type is wrong, or the "
                        "body is malformed!"
                    )
                )
                return None
        else:
            return None

    @property
    def raw_text(self):
        """
        Get the verbatim error message received from a ArkID API as a *string*
        """
        return self._underlying_response.text

    def _get_args(self):
        """
        Get arguments to pass to the Exception base class. These args are
        displayed in stack traces.
        """
        return self.http_status, self.code, self.message

    def _load_from_json(self, data):
        """
        Load error data from a JSON document. Must set at least
        code and message instance variables.
        """

    def _load_from_text(self, text):
        """
        Load error data from a raw text body that is not JSON. Must set at
        least code and message instance variables.
        """


class UserAPIError(ArkIDAPIError):
    """
    Error class for the User API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides:

    :ivar error_data: Additional object returned in the error response. May be
                      a dict, list, or None.
    """

    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.code, self.message


class ConfigAPIError(ArkIDAPIError):
    """
    Error class for the Config API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides:

    :ivar error_data: Additional object returned in the error response. May be
                      a dict, list, or None.
    """

    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.code, self.message


class AuthAPIError(ArkIDAPIError):
    """
    Error class for the API components of Globus Auth.

    Customizes JSON parsing.
    """


# Wrappers around requests exceptions, so the SDK is API independent.
class NetworkError(ArkIDError):
    """
    Error communicating with the REST API server.

    Holds onto original exception data, but also takes a message
    to explain potentially confusing or inconsistent exceptions passed to us
    """

    def __init__(self, message, exception, *args, **kwargs):
        super(NetworkError, self).__init__(message)
        self.underlying_exception = exception


class ArkIDTimeoutError(NetworkError):
    """The REST request timed out."""


class ArkIDConnectionTimeoutError(ArkIDTimeoutError):
    """The request timed out during connection establishment.
    These errors are safe to retry."""


class ArkIDConnectionError(NetworkError):
    """A connection error occurred while making a REST request."""


def convert_request_exception(exception):
    """Converts incoming requests.Exception to a ArkID NetworkError"""

    if isinstance(exception, requests.ConnectTimeout):
        return ArkIDConnectionTimeoutError("Connection Timeout Error on request", exception)

    if isinstance(exception, requests.Timeout):
        return ArkIDTimeoutError("Timeout Error on request", exception)

    elif isinstance(exception, requests.ConnectionError):
        return ArkIDConnectionError("Connection Error on request", exception)

    return NetworkError("Network Error on request", exception)
