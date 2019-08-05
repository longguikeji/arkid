"""
Dingding operation failed shall raise an exception
"""


class APICallError(Exception):
    """
    exception describe dingding operation fail reason
    """

    def __init__(self, error_info):
        super(APICallError, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return 'API call error occur:' + self.error_info
