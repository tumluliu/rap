"""Python class file of fetching routes from Google Maps Directions API
"""

import logging
import json
from time import sleep
import googlemaps
from .base import RoutingService

LOGGER = logging.getLogger(__name__)


class GoogleMapsRouter(RoutingService):
    """ Wrapper class of Google Maps Services Python client

    For more details, visit the official documentation page:
    https://github.com/googlemaps/google-maps-services-python
    """

    profile_dict = {
        "driving": "driving",
        "walking": "walking",
        "cycling": "bicycling"
    }

    def __init__(self, profile, api_key, rate_limit=-1, cache=None):
        LOGGER.debug(
            "GoogleMapsRouter __init__ with %s, %s, %s and %s arguments passed in",
            profile, api_key, cache, rate_limit)
        if profile not in self.profile_dict:
            # The profile passed in is not supported by Google Maps routing service
            return None
        # TODO (lliu) Should support quota in the future
        # but it's not easy
        # self.daily_quota = 2500
        self.profile = self.profile_dict[profile]
        self.coordinates = ""
        self.params = {}
        self.gmaps = googlemaps.Client(key=api_key)

        # Request directions via public transit
        LOGGER.debug("The input profile %s has been converted to %s",
                     profile, self.profile)
        super(GoogleMapsRouter, self).__init__(api_key, cache, rate_limit)

    def find_path(self, source_lng, source_lat, target_lng, target_lat,
                  params=None):
        """ Find the optimal path with Google Maps Directions HTTP API

        :param float source_lng: longitude value of the starting position
        :param float source_lat: latitude value of the starting position
        :param float target_lng: longitude value of the ending position
        :param float target_lat: latitude value of the ending position
        :param Dict params: the other query parameters for Google Maps router
        :return: None for no path found; a JSON object for the found path info
        """
        directions_result = self.gmaps.directions("{0},{1}".format(source_lat, source_lng),
                                                  "{0},{1}".format(
                                                      target_lat, target_lng),
                                                  mode=self.profile)
        LOGGER.info("Sending request to Google Maps Directions API server")
        if self.rate_limit > 0:
            sleep(1 / self.rate_limit)
        for r in directions_result:
            LOGGER.debug("Get routes: %s", str(r))
        if not directions_result:
            LOGGER.info("No path found")
            return None

        return json.dumps(directions_result)
