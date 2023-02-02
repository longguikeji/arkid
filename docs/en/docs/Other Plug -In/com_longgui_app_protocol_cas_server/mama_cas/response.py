import datetime

from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_str

from .compat import etree


class CasResponseBase(HttpResponse):
    """
    Base class for CAS 2.0 XML format responses.
    """
    prefix = 'cas'
    uri = 'http://www.yale.edu/tp/cas'

    def __init__(self, context, **kwargs):
        etree.register_namespace(self.prefix, self.uri)
        content = self.render_content(context)
        super(CasResponseBase, self).__init__(content, **kwargs)

    def ns(self, tag):
        """
        Given an XML tag, output the qualified name for proper
        namespace handling on output.
        """
        return etree.QName(self.uri, tag)


class ValidationResponse(CasResponseBase):
    """
    (2.6.2) Render an XML format CAS service response for a
    ticket validation success or failure.

    On validation success:

    <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
        <cas:authenticationSuccess>
            <cas:user>username</cas:user>
            <cas:proxyGrantingTicket>PGTIOU-84678-8a9d...</cas:proxyGrantingTicket>
            <cas:proxies>
                <cas:proxy>https://proxy2/pgtUrl</cas:proxy>
                <cas:proxy>https://proxy1/pgtUrl</cas:proxy>
            </cas:proxies>
        </cas:authenticationSuccess>
    </cas:serviceResponse>

    On validation failure:

    <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
        <cas:authenticationFailure code="INVALID_TICKET">
            ticket PT-1856376-1HMgO86Z2ZKeByc5XdYD not recognized
        </cas:authenticationFailure>
    </cas:serviceResponse>
    """
    def render_content(self, context):
        ticket = context.get('ticket')
        error = context.get('error')
        attributes = context.get('attributes')
        pgt = context.get('pgt')
        proxies = context.get('proxies')

        service_response = etree.Element(self.ns('serviceResponse'))
        if ticket:
            auth_success = etree.SubElement(service_response, self.ns('authenticationSuccess'))
            user = etree.SubElement(auth_success, self.ns('user'))
            user.text = ticket.user.username
            if attributes:
                attribute_set = etree.SubElement(auth_success, self.ns('attributes'))
                for name, value in attributes.items():
                    if isinstance(value, list):
                        for v in value:
                            attr = etree.SubElement(attribute_set, self.ns(name))
                            attr.text = force_str(v)
                    else:
                        attr = etree.SubElement(attribute_set, self.ns(name))
                        attr.text = force_str(value)
            if pgt:
                proxy_granting_ticket = etree.SubElement(auth_success, self.ns('proxyGrantingTicket'))
                proxy_granting_ticket.text = pgt.iou
            if proxies:
                proxy_list = etree.SubElement(auth_success, self.ns('proxies'))
                for p in proxies:
                    proxy = etree.SubElement(proxy_list, self.ns('proxy'))
                    proxy.text = p
        elif error:  # pragma: no branch
            auth_failure = etree.SubElement(service_response, self.ns('authenticationFailure'))
            auth_failure.set('code', error.code)
            auth_failure.text = str(error)

        return etree.tostring(service_response, encoding='UTF-8')


class ProxyResponse(CasResponseBase):
    """
    (2.7.2) Render an XML format CAS service response for a proxy
    request success or failure.

    On request success:

    <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
        <cas:proxySuccess>
            <cas:proxyTicket>PT-1856392-b98xZrQN4p90ASrw96c8</cas:proxyTicket>
        </cas:proxySuccess>
    </cas:serviceResponse>

    On request failure:

    <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
        <cas:proxyFailure code="INVALID_REQUEST">
            'pgt' and 'targetService' parameters are both required
        </cas:proxyFailure>
    </cas:serviceResponse>
    """
    def render_content(self, context):
        ticket = context.get('ticket')
        error = context.get('error')

        service_response = etree.Element(self.ns('serviceResponse'))
        if ticket:
            proxy_success = etree.SubElement(service_response, self.ns('proxySuccess'))
            proxy_ticket = etree.SubElement(proxy_success, self.ns('proxyTicket'))
            proxy_ticket.text = ticket.ticket
        elif error:  # pragma: no branch
            proxy_failure = etree.SubElement(service_response, self.ns('proxyFailure'))
            proxy_failure.set('code', error.code)
            proxy_failure.text = str(error)

        return etree.tostring(service_response, encoding='UTF-8')


class SamlValidationResponse(CasResponseBase):
    """
    (4.2.5) Render a SAML 1.1 response for a service ticket validation
    success or failure.
    """
    prefix = 'SOAP-ENV'
    uri = 'http://schemas.xmlsoap.org/soap/envelope/'
    namespace = 'http://www.ja-sig.org/products/cas/'
    authn_method_password = 'urn:oasis:names:tc:SAML:1.0:am:password'
    confirmation_method = 'urn:oasis:names:tc:SAML:1.0:cm:artifact'

    def __init__(self, context, **kwargs):
        self._instant = datetime.datetime.utcnow()
        super(SamlValidationResponse, self).__init__(context, **kwargs)

    def instant(self, instant=None, offset=None):
        if not instant:
            instant = self._instant
        if offset:
            instant = instant + datetime.timedelta(seconds=offset)
        return instant.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def generate_id(self):
        return '_' + get_random_string(length=32,
                                       allowed_chars='abcdef0123456789')

    def render_content(self, context):
        ticket = context.get('ticket')
        attributes = context.get('attributes')
        error = context.get('error')

        envelope = etree.Element(self.ns('Envelope'))
        etree.SubElement(envelope, self.ns('Header'))
        body = etree.SubElement(envelope, self.ns('Body'))
        response = etree.SubElement(body, 'Response')
        response.set('xmlns', 'urn:oasis:names:tc:SAML:1.0:protocol')
        response.set('xmlns:saml', 'urn:oasis:names:tc:SAML:1.0:assertion')
        response.set('xmlns:samlp', 'urn:oasis:names:tc:SAML:1.0:protocol')
        response.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        response.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        response.set('IssueInstant', self.instant())
        response.set('MajorVersion', '1')
        response.set('MinorVersion', '1')
        response.set('ResponseID', self.generate_id())
        if ticket:
            response.set('Recipient', ticket.service)
            response.append(self.get_status('Success'))
            response.append(self.get_assertion(ticket, attributes))
        elif error:  # pragma: no branch
            response.set('Recipient', 'UNKNOWN')
            response.append(self.get_status('RequestDenied', message=str(error)))
        return etree.tostring(envelope, encoding='UTF-8')

    def get_status(self, status_value, message=None):
        """
        Build a Status XML block for a SAML 1.1 Response.
        """
        status = etree.Element('Status')
        status_code = etree.SubElement(status, 'StatusCode')
        status_code.set('Value', 'samlp:' + status_value)
        if message:
            status_message = etree.SubElement(status, 'StatusMessage')
            status_message.text = message
        return status

    def get_assertion(self, ticket, attributes):
        """
        Build a SAML 1.1 Assertion XML block.
        """
        assertion = etree.Element('Assertion')
        assertion.set('xmlns', 'urn:oasis:names:tc:SAML:1.0:assertion')
        assertion.set('AssertionID', self.generate_id())
        assertion.set('IssueInstant', self.instant())
        assertion.set('Issuer', 'localhost')
        assertion.set('MajorVersion', '1')
        assertion.set('MinorVersion', '1')
        assertion.append(self.get_conditions(ticket.service))
        subject = self.get_subject(ticket.user.get_username())
        if attributes:
            assertion.append(self.get_attribute_statement(subject, attributes))
        assertion.append(self.get_authentication_statement(subject, ticket))

        return assertion

    def get_conditions(self, service_id):
        """
        Build a Conditions XML block for a SAML 1.1 Assertion.
        """
        conditions = etree.Element('Conditions')
        conditions.set('NotBefore', self.instant())
        conditions.set('NotOnOrAfter', self.instant(offset=30))
        restriction = etree.SubElement(conditions, 'AudienceRestrictionCondition')
        audience = etree.SubElement(restriction, 'Audience')
        audience.text = service_id
        return conditions

    def get_attribute_statement(self, subject, attributes):
        """
        Build an AttributeStatement XML block for a SAML 1.1 Assertion.
        """
        attribute_statement = etree.Element('AttributeStatement')
        attribute_statement.append(subject)
        for name, value in attributes.items():
            attribute = etree.SubElement(attribute_statement, 'Attribute')
            attribute.set('AttributeName', name)
            attribute.set('AttributeNamespace', self.namespace)
            if isinstance(value, list):
                for v in value:
                    attribute_value = etree.SubElement(attribute, 'AttributeValue')
                    attribute_value.text = force_str(v)
            else:
                attribute_value = etree.SubElement(attribute, 'AttributeValue')
                attribute_value.text = force_str(value)
        return attribute_statement

    def get_authentication_statement(self, subject, ticket):
        """
        Build an AuthenticationStatement XML block for a SAML 1.1
        Assertion.
        """
        authentication_statement = etree.Element('AuthenticationStatement')
        authentication_statement.set('AuthenticationInstant',
                                     self.instant(instant=ticket.consumed))
        authentication_statement.set('AuthenticationMethod',
                                     self.authn_method_password)
        authentication_statement.append(subject)
        return authentication_statement

    def get_subject(self, identifier):
        """
        Build a Subject XML block for a SAML 1.1
        AuthenticationStatement or AttributeStatement.
        """
        subject = etree.Element('Subject')
        name = etree.SubElement(subject, 'NameIdentifier')
        name.text = identifier
        subject_confirmation = etree.SubElement(subject, 'SubjectConfirmation')
        method = etree.SubElement(subject_confirmation, 'ConfirmationMethod')
        method.text = self.confirmation_method
        return subject
