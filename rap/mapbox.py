"""Python class file of fetching routes from Mapbox's Directions API
"""

import logging
import json
from time import sleep
from uritemplate import URITemplate
from .base import RoutingService

LOGGER = logging.getLogger(__name__)


class MapboxRouter(RoutingService):
    """ Wrapper class of Mapbox direction http API v5

    The mapbox-sdk-py is not used because it's out of date
    and lacks maintenance.
    For more details, visit the official documentation page:
    https://www.mapbox.com/api-documentation/?language=cURL#directions

    Sample request URL:
    https://api.mapbox.com/directions/v5/mapbox/cycling/-122.42,37.78;-77.03,38.91?access_token=your-access-token
    https://api.mapbox.com/directions/v5/mapbox/driving/13.4301,52.5109;13.4265,52.5080;13.4194,52.5072?radiuses=40;;100&geometries=polyline&access_token=your-access-token
    """

    v5_baseuri = "https://api.mapbox.com/directions/v5/mapbox"
    api_uri_template = URITemplate(v5_baseuri + "{/profile}{/coordinates}")
    profile_dict = {
        "driving": "driving",
        "walking": "walking",
        "cycling": "cycling"
    }

    def __init__(self, profile, api_key, cache=None, rate_limit=-1):
        LOGGER.debug(
            "MapboxRouter __init__ with %s, %s and %s arguments passed in",
            profile, api_key, cache)
        if profile not in self.profile_dict:
            # The profile passed in is not supported by Mapbox routing service
            return None
        self.profile = self.profile_dict[profile]
        self.coordinates = ""
        self.params = {}
        LOGGER.debug("The input profile %s has been converted to %s",
                     profile, self.profile)
        super(MapboxRouter, self).__init__(api_key, cache, rate_limit)

    def find_path(self, source_lng, source_lat, target_lng, target_lat,
                  params=None):
        """ Find the optimal path with Mapbox Directions HTTP API

        :param float source_lng: longitude value of the starting position
        :param float source_lat: latitude value of the starting position
        :param float target_lng: longitude value of the ending position
        :param float target_lat: latitude value of the ending position
        :param Dict params: the other query parameters for the mapbox router
        :return: None for no path found; a JSON object for the found path info
        """
        self.coordinates = "{0},{1};{2},{3}".format(source_lng, source_lat,
                                                    target_lng, target_lat)
        self.params = {} if params is None else params
        self.params.update({'access_token': self.api_key})

        uri = self.api_uri_template.expand({
            'profile': self.profile,
            'coordinates': self.coordinates
        })
        LOGGER.info("Sending request to Mapbox Directions API server")
        LOGGER.debug("Query string parameters are: %s", str(self.params))
        if self.rate_limit > 0:
            sleep(1 / self.rate_limit)
        resp = self.session.get(uri, params=self.params)
        LOGGER.debug("Get response %s", resp.text)
        if resp.status_code != 200:
            LOGGER.error("Error occurs with code %s", resp.status_code)
            return None
        else:
            mapbox_status_code = json.loads(resp.text)['code']
            if str.lower(mapbox_status_code) != 'ok':
                LOGGER.info("No path found")
                return None

        self.handle_http_error(resp)
        return json.loads(resp.text)
