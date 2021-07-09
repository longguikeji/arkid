"""
SAML2.0协议登陆流程
"""
from saml2.authn_context import PASSWORD, AuthnBroker, authn_context_class_ref

def get_authn(req_info=None):
    """
    获取登陆状态
    """
    req_authn_context = req_info.message.requested_authn_context if req_info else PASSWORD
    broker = AuthnBroker()
    broker.add(authn_context_class_ref(req_authn_context), "")
    return broker.get_authn_by_accr(req_authn_context)
    