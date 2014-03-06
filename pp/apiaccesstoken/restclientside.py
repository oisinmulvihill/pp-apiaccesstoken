# -*- coding: utf-8 -*-
"""
"""
import logging

import requests

from pp.apiaccesstoken.headers import ACCESS_TOKEN_HEADER


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


class RequestsAccessTokenAuth(requests.auth.AuthBase):
    """Handles the setting of X-API-ACCESS-TOKEN in the request header.

    This can be passed to the requests auth field for use against our
    servers.

    """
    def __init__(self, access_token):
        self.log = get_log('AccessTokenAuth')
        self.access_token = access_token

    def __call__(self, r):
        self.log.debug("Adding access token to request header.")
        r.headers[ACCESS_TOKEN_HEADER.lstrip('HTTP')] = self.access_token
        return r
