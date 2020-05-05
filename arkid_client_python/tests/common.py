# -*- coding: utf8 -*-
"""
Common use helpers and utilities for all tests to leverage.
Not so disorganized as a "utils" module and not so refined as a public package.
"""

import httpretty
from arkid_client.base import slash_join


# end constants
def register_api_route(service, base_url, path, method=httpretty.GET, adding_headers=None, **kwargs):
    """
    Handy wrapper for adding URIs to the HTTPretty state.
    """
    assert httpretty.is_enabled()
    service_map = {
        'ucenter': 'ucenter',
        'auth': 'auth',
        'revoke': 'revoke',
        'user': 'user',
        'org': 'org',
        'node': 'node',
        'perm': 'perm',
        'app': 'app',
        'infrastructure': 'service',
    }
    assert service in service_map
    base_url = slash_join(base_url, service_map.get(service))
    full_url = slash_join(base_url, path)

    # can set it to `{}` explicitly to clear the default
    if adding_headers is None:
        adding_headers = {'Content-Type': 'application/json'}

    httpretty.register_uri(method, full_url, adding_headers=adding_headers, **kwargs)
