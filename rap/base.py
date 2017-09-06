"""Base routing service class"""

import requests
from cachecontrol import CacheControl
from . import __version__
from . import errors


def Session():
    """Returns an HTTP session.
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'rap/{0} {1}'.format(__version__,
                                           requests.utils.default_user_agent())
    })
    return session


class RoutingService(object):
    """Routing service base class.
    """

    def __init__(self, api_key=None, cache=None, rate_limit=-1):
        """Constructs a routing service object.

        :param api_key: API key for a routing service if needed
        :param cache: CacheControl cache instance (Dict or FileCache).
        """
        self.api_key = api_key
        self.session = Session()
        self.rate_limit = rate_limit
        if cache:
            self.session = CacheControl(self.session, cache=cache)

    def handle_http_error(self,
                          response,
                          custom_messages=None,
                          raise_for_status=False):
        """ Error handler
        """
        if not custom_messages:
            custom_messages = {}
        if response.status_code in custom_messages.keys():
            raise errors.HTTPError(custom_messages[response.status_code])
        if raise_for_status:
            response.raise_for_status()
