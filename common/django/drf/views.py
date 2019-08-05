
import functools

from json.decoder import JSONDecodeError
from rest_framework.exceptions import ParseError


def catch_json_load_error(func):
    '''
    JSONDecodeError -> ParseError(400)
    '''
    @functools.wraps(func)
    def wraper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JSONDecodeError:
            raise ParseError
    return wraper
