# -*- coding: utf-8 -*-
"""
"""

from pp.apiaccesstoken.restclientside import RequestsAccessTokenAuth


def test_usage_of_RequestsAccessTokenAuth():
    """Test how the RequestsAccessTokenAuth will be used by requests lib.
    """

    class MockRequest(object):
        headers = {}

    req = MockRequest()

    access_token = "a fake access token"

    assert RequestsAccessTokenAuth.HEADER_FIELD == 'X-API-ACCESS-TOKEN'

    rata = RequestsAccessTokenAuth(access_token)

    assert rata.access_token == access_token

    rata(req)

    assert RequestsAccessTokenAuth.HEADER_FIELD in req.headers

    v = req.headers[RequestsAccessTokenAuth.HEADER_FIELD]
    assert v == access_token
