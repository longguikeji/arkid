#!/usr/bin/env python3


"""Errors that can be raised by this SDK"""


class ScimClientError(Exception):
    """Base class for Client errors"""


class BotUserAccessError(ScimClientError):
    """Error raised when an 'xoxb-*' token is
    being used for a Scim API method that only accepts 'xoxp-*' tokens.
    """


class ScimRequestError(ScimClientError):
    """Error raised when there's a problem with the request that's being submitted."""


class ScimApiError(ScimClientError):
    """Error raised when Scim does not send the expected response.

    Attributes:
        response (ScimResponse): The ScimResponse object containing all of the data sent back from the API.

    Note:
        The message (str) passed into the exception is used when
        a user converts the exception to a str.
        i.e. str(ScimApiError("This text will be sent as a string."))
    """

    def __init__(self, message, response):
        msg = f"{message}\nThe server responded with: {response}"
        self.response = response
        super(ScimApiError, self).__init__(msg)


class ScimClientNotConnectedError(ScimClientError):
    """Error raised when attempting to send messages over the websocket when the
    connection is closed."""


class ScimObjectFormationError(ScimClientError):
    """Error raised when a constructed object is not valid/malformed"""


class ScimClientConfigurationError(ScimClientError):
    """Error raised when attempting to send messages over the websocket when the
    connection is closed."""
