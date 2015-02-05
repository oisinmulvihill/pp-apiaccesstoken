# -*- coding: utf-8 -*-
"""
"""
from pp.apiaccesstoken.headers import ACCESS_TOKEN_HEADER
from pp.apiaccesstoken.headers import WSGI_ENV_ACCESS_TOKEN_HEADER
from pp.apiaccesstoken.restclientside import RequestsAccessTokenAuth


def test_usage_of_RequestsAccessTokenAuth():
    """Test how the RequestsAccessTokenAuth will be used by requests lib.
    """

    class MockRequest(object):
        headers = {}

    req = MockRequest()

    access_token = "a fake access token"

    assert ACCESS_TOKEN_HEADER == 'AUTHORIZATION'

    rata = RequestsAccessTokenAuth(access_token)

    assert rata.access_token == access_token

    rata(req)

    assert ACCESS_TOKEN_HEADER in req.headers

    v = req.headers[ACCESS_TOKEN_HEADER]
    assert v == "Token {}".format(access_token)
