"""Base routing service class"""

import requests
from cachecontrol import CacheControl
from . import __version__
from . import errors


def Session(api_key=None):
    """Returns an HTTP session.

    :param api_key: Mapbox access token string (optional).
    """
    session = requests.Session()
    session.params.update(api_key=api_key)
    session.headers.update({
        'User-Agent': 'rap/{0} {1}'.format(__version__,
                                           requests.utils.default_user_agent())
    })
    return session


class RoutingService(object):
    """Routing service base class.
    """

    def __init__(self, api_key=None, cache=None):
        """Constructs a Service object.

        :param api_key: API key for a routing service
        :param cache: CacheControl cache instance (Dict or FileCache).
        """
        self.session = Session(api_key)
        if cache:
            self.session = CacheControl(self.session, cache=cache)

    def handle_http_error(self,
                          response,
                          custom_messages=None,
                          raise_for_status=False):
        if not custom_messages:
            custom_messages = {}
        if response.status_code in custom_messages.keys():
            raise errors.HTTPError(custom_messages[response.status_code])
        if raise_for_status:
            response.raise_for_status()
