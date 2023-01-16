# Prefer cElementTree for performance, but fall back to the Python
# implementation in case C extensions are not available.
try:
    import xml.etree.cElementTree as etree
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as etree


# requests-futures is optional, and allows for asynchronous single logout
# requests. If it is not present, synchronous requests will be sent.
try:
    from requests_futures.sessions import FuturesSession as Session
except ImportError:  # pragma: no cover
    from requests import Session


# defusedxml is optional, and is used for the /samlValidate
# endpoint. If it is not present, this endpoint raises an exception.
try:
    import defusedxml.ElementTree as defused_etree
except ImportError:  # pragma: no cover
    defused_etree = None
