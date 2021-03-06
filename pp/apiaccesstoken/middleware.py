# -*- coding: utf-8 -*-
"""
"""
import re
import logging

from pp.apiaccesstoken.tokenmanager import Manager
from pp.apiaccesstoken.tokenmanager import AccessTokenInvalid
from pp.apiaccesstoken.headers import WSGI_ENV_ACCESS_TOKEN_HEADER


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


def recover_secret(access_token):
    """Given the access_token recover the access_secret to verify it with.

    :params access_secret: The access token string.

    :returns: access_secret on success or None on failure.

    """
    raise NotImplementedError('No Valid Access Detail Recovery Provided')


WITHTOKEN_RE = re.compile("(Token\s*)(.*)")


class ValidateAccessToken(object):
    """Validate and API access token and populate the wsgi environment with
    the identity recovered.

    ValidateAccessToken.HTTP_HEADER is the name of the wsgi env variable to
    look for.

    ValidateAccessToken.ENV_KEY is the name wsgi env variable to store
    the identity in. The value of the identity is recovered from the 'identity'
    field in the access_token payload.

    The constructor for this class takes a recover_secret() function. This
    needs to be provided or NotImplementedError will be raised. This function
    recovers the access_secret for the given access_token if any. If this
    function returns None then nothing was recovered and the token is invalid.

    """
    # The wsgi environment variable to set when an identity was found:
    ENV_KEY = 'pp.api_access.identity'

    def __init__(
        self, application, recover_secret=recover_secret
    ):
        self.log = get_log('ValidateAccessToken')
        self.application = application
        self.recover_secret = recover_secret

    def recover_access(self, environ, access_token):
        """Populate the environment with the user identity recovered from the
        payload of the access_token.

        To get the payload the access_token needs its corresponding
        access_secret to recover it.

        """
        log = get_log('ValidateAccessToken.recover_access')

        # log.debug("recovering the access_secret for access_token:{}".format(
        #     access_token
        # ))
        try:
            access_secret = self.recover_secret(access_token)
            if access_secret:
                # log.debug(
                #     "access_secret for access_token:{} recovered OK.".format(
                #         access_token
                #     )
                # )
                man = Manager(access_secret)
                payload = man.verify_access_token(access_token)
                # log.debug(
                #     "Payload recovered '{}'. Looking for identity.".format(
                #         access_token
                #     )
                # )

                identity = payload['identity']
                # self.log.debug(
                #     "Token Valid. Adding identity '{}' environ.".format(
                #         identity
                #     )
                # )
                environ[self.ENV_KEY] = identity

            else:
                self.log.info(
                    (
                        "No secret recovered for access_token '{}'. "
                        "Ignoring token."
                    ).format(
                        access_token
                    )
                )

        except AccessTokenInvalid, e:
            log.error(
                "token validation fail: '{}'".format(e)
            )

        except Exception, e:
            log.exception(
                "General error validating token: '{}'".format(e)
            )

    def token_extract(self, header_value):
        """Handle 'Token <data>' or '<data>' values in the auth header content.

        :returns: the <data> bit of the header_value.

        """
        access_token = ""

        with_token = re.match(WITHTOKEN_RE, header_value)
        if with_token:
            access_token = with_token.groups()[1]

        else:
            access_token = header_value.strip()

        return access_token

    def __call__(self, environ, start_response):
        """Wsgi hook into kicking off the token validation and identity
        recovery.

        """
        # log = get_log("ValidateAccessToken")

        access_token = environ.get(WSGI_ENV_ACCESS_TOKEN_HEADER)
        if not access_token:
            access_token = environ.get("HTTP_AUTHORIZATION")

        # log.debug("PATH_INFO: '{}'".format(environ.get("PATH_INFO")))

        if access_token:
            # String out the "Token " from the "Token <token key>" from the
            # HTTP_AUTHORIZATION string.
            access_token = self.token_extract(access_token)
            self.recover_access(environ, access_token)

        # else:
        #     log.debug(
        #         "AUTHORIZATION not found in environ: {}".format(
        #             environ.items()
        #         )
        #     )

        return self.application(environ, start_response)
