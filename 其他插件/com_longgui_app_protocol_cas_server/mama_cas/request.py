import datetime

from django.utils.crypto import get_random_string

from .compat import etree


class CasRequestBase(object):
    """
    Base class for CAS 3.1 SAML format requests.
    """
    prefixes = {}

    def __init__(self, context):
        self.context = context
        for prefix, uri in self.prefixes.items():
            etree.register_namespace(prefix, uri)

    def ns(self, prefix, tag):
        """
        Given a prefix and an XML tag, output the qualified name
        for proper namespace handling on output.
        """
        return etree.QName(self.prefixes[prefix], tag)

    def instant(self):
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class SingleSignOutRequest(CasRequestBase):
    """
    [CAS 3.0] Render a SAML single sign-off request, to be sent to a
    service URL during a logout event.

    An example request:

    <samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="[RANDOM ID]"
    Version="2.0" IssueInstant="[CURRENT DATE/TIME]">
        <saml:NameID>@NOT_USED@</saml:NameID>
        <samlp:SessionIndex>[SESSION IDENTIFIER]</samlp:SessionIndex>
    </samlp:LogoutRequest>
    """
    prefixes = {'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion'}

    def render_content(self):
        ticket = self.context.get('ticket')

        logout_request = etree.Element(self.ns('samlp', 'LogoutRequest'))
        logout_request.set('ID', get_random_string(length=32))
        logout_request.set('Version', '2.0')
        logout_request.set('IssueInstant', self.instant())
        etree.SubElement(logout_request, self.ns('saml', 'NameID'))
        session_index = etree.SubElement(logout_request, self.ns('samlp', 'SessionIndex'))
        session_index.text = ticket.ticket

        return etree.tostring(logout_request)


class SamlValidateRequest(CasRequestBase):
    """
    [CAS 3.0] Render a /samlValidate endpoint request, to be used for
    testing purposes. This is not used for server operation.

    An example request:

    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
        <SOAP-ENV:Header/>
        <SOAP-ENV:Body>
            <samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"
            MajorVersion="1" MinorVersion="1" RequestID="_192.168.16.51.1024506224022"
            IssueInstant="2002-06-19T17:03:44.022Z">
                <samlp:AssertionArtifact>
                    ST-1-u4hrm3td92cLxpCvrjylcas.example.com
                </samlp:AssertionArtifact>
            </samlp:Request>
        </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
    """
    prefixes = {'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/',
                'samlp': 'urn:oasis:names:tc:SAML:1.0:protocol'}

    def render_content(self):
        envelope = etree.Element(self.ns('SOAP-ENV', 'Envelope'))
        etree.SubElement(envelope, self.ns('SOAP-ENV', 'Header'))
        body = etree.SubElement(envelope, self.ns('SOAP-ENV', 'Body'))
        body.append(self.get_request())
        return etree.tostring(envelope, encoding='UTF-8')

    def get_request(self):
        ticket = self.context.get('ticket')

        request = etree.Element(self.ns('samlp', 'Request'))
        request.set('MajorVersion', '1')
        request.set('MinorVersion', '1')
        request.set('RequestID', get_random_string(length=32))
        request.set('IssueInstant', self.instant())
        artifact = etree.SubElement(request, self.ns('samlp', 'AssertionArtifact'))
        artifact.text = ticket.ticket
        return request
