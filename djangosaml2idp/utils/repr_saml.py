"""
SAML2 协议 解码
"""
import base64
import xml.dom.minidom
import zlib
from xml.parsers.expat import ExpatError

def repr_saml(saml: str, b64: bool = False):
    """ Decode SAML from b64 and b64 deflated and return a pretty printed representation
    """
    try:
        msg = base64.b64decode(saml).decode() if b64 else saml
        dom = xml.dom.minidom.parseString(msg)
    except (UnicodeDecodeError, ExpatError):
        # in HTTP-REDIRECT the base64 must be inflated
        compressed = base64.b64decode(saml)
        inflated = zlib.decompress(compressed, -15)
        dom = xml.dom.minidom.parseString(inflated.decode())
    return dom.toprettyxml()
    