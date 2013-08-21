# -*- coding: utf-8 -*-
"""
"""
import pytest

from pp.apiaccesstoken import tokenmanager
from pp.apiaccesstoken.middleware import ValidateAccessToken


class MockApp(object):
    """Mock wsgi app."""

    def __call__(self, environ, start_response):
        pass


class FakeSecretRecover(object):

    def __init__(self, access_secret):
        self.recover_secret_called = False
        self.access_secret = access_secret
        self.access_token_given = None

    def recover_secret(self, access_token):
        self.access_token_given = access_token
        return self.access_secret


def test_ValidateAccessToken():
    """Test the middleware ValidateAccessToken usage.
    """
    username = 'fran'
    access_secret = tokenmanager.Manager.generate_secret()
    man = tokenmanager.Manager(access_secret)
    access_token = man.generate_access_token(identity=username)

    fsr = FakeSecretRecover(access_secret)
    assert fsr.access_secret == access_secret
    assert fsr.access_token_given is None

    app = MockApp()
    vat = ValidateAccessToken(app, recover_secret=fsr.recover_secret)

    assert vat.ENV_KEY == 'pp.api_access.identity'
    assert vat.HTTP_HEADER == "HTTP_X_API_ACCESS_TOKEN"

    environ = {}
    start_response = lambda x: x

    # make a wsgi call which will result in no action:
    vat(environ, start_response)

    # check nothing has changed:
    assert fsr.access_secret == access_secret
    assert fsr.access_token_given is None
    assert ValidateAccessToken.ENV_KEY not in environ

    # Now provide and access token which is valid:
    #
    environ[ValidateAccessToken.HTTP_HEADER] = access_token
    vat(environ, start_response)

    # Now the identity should have been recovered and set in the env:
    assert fsr.access_secret == access_secret
    assert fsr.access_token_given == access_token
    assert ValidateAccessToken.ENV_KEY in environ
    assert environ[ValidateAccessToken.ENV_KEY] == username


def test_ValidateAccessToken_invalid_secet():
    """Test the middleware ValidateAccessToken usage.
    """
    username = 'fran'
    access_secret = tokenmanager.Manager.generate_secret()
    man = tokenmanager.Manager(access_secret)
    environ = {}
    start_response = lambda x: x
    access_token = man.generate_access_token(identity=username)

    fsr = FakeSecretRecover("the wrong secret")
    assert fsr.access_secret == "the wrong secret"
    assert fsr.access_token_given is None

    app = MockApp()
    vat = ValidateAccessToken(app, recover_secret=fsr.recover_secret)

    # make a wsgi call which will result in no action:
    vat(environ, start_response)

    # check nothing has changed:
    assert fsr.access_secret == "the wrong secret"
    assert fsr.access_token_given is None
    assert ValidateAccessToken.ENV_KEY not in environ

    # Now provide the access token:
    environ[ValidateAccessToken.HTTP_HEADER] = access_token
    vat(environ, start_response)

    # The identity should not be in the environment as the payload won't
    # have been recovered, the secret should not have been able to decode
    # the token.
    assert fsr.access_secret == "the wrong secret"
    assert fsr.access_token_given == access_token
    assert ValidateAccessToken.ENV_KEY not in environ


def test_tokenmanager():
    """Test the basic usage and calls of the manager.
    """
    username = 'fran'

    secret = tokenmanager.Manager.generate_secret()

    man = tokenmanager.Manager(secret)

    # Generate an access_token, this needs the master secret set so can't be
    # a class
    access_token = man.generate_access_token(identity=username)

    # Some time later...

    # Now verify the access token
    man1 = tokenmanager.Manager(secret)

    payload = man1.verify_access_token(access_token)

    #print "payload: ", payload

    assert payload['identity'] == username
    # Hard coded for the moment as I'm forcing tokens not to expire.
    assert payload['expires'] == 10

    # an invalid token will raise and exception
    with pytest.raises(tokenmanager.AccessTokenInvalid):
        man1.verify_access_token("some token I've just made up.")

    # the master secret needs to be the same as that generating secrets:
    with pytest.raises(tokenmanager.AccessTokenInvalid):
        man2 = tokenmanager.Manager("the wrong secret key")
        man2.verify_access_token(access_token)
