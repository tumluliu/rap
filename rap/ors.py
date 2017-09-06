"""Python class file of fetching routes from OpenRouteService's Directions API
"""

import logging
import json
from time import sleep
from uritemplate import URITemplate
from .base import RoutingService

LOGGER = logging.getLogger(__name__)


class OpenRouteServiceRouter(RoutingService):
    """ Wrapper class of OpenRouteService direction http API v4.3.0

    For more information about the API, visit the following pages:
    https://openrouteservice.org
    https://app.swaggerhub.com/apis/OpenRouteService/ors-api

    Sample request URL:
    https://api.openrouteservice.org/directions?&coordinates=8.83910179,49.5704409%7c8.854132889999988,49.614509&instructions=false&profile=cycling-regular&api_key=ORS_API_KEY
    """

    ors_baseuri = "https://api.openrouteservice.org/directions"
    api_uri_template = URITemplate(ors_baseuri)
    profile_dict = {
        "driving": ["driving-car", "driving-hgv"],
        "driving.car": "driving-car",
        "driving.hgv": "driving-hgv",
        "walking": ["foot-walking", "foot-hiking"],
        "walking.normal": "foot-walking",
        "walking.hiking": "foot-hiking",
        "cycling": ["cycling-regular", "cycling-road", "cycling-safe", "cycling-mountain", "cycling-tour", "cycling-electric"],
        "cycling.normal": "cycling-regular",
        "cycling.road": "cycling-road",
        "cycling.safe": "cycling-safe",
        "cycling.mountain": "cycling-mountain",
        "cycling.tour": "cycling-tour",
        "cycling.ebike": "cycling-electric"
    }
    # For internal ORS developer, it's unlimited ;)
    request_interval = 1 / super.rate_limit

    def __init__(self, profile, api_key, cache=None):
        LOGGER.debug(
            "OpenRouteServiceRouter __init__ with %s, %s and %s arguments passed in",
            profile, api_key, cache)
        if profile not in self.profile_dict.keys():
            # The profile passed in is not supported by Mapbox routing service
            return None
        self.profile = self.profile_dict[profile]
        self.coordinates = ""
        self.params = {}
        LOGGER.debug("The input profile %s has been converted to %s",
                     profile, self.profile)
        super(OpenRouteServiceRouter, self).__init__(api_key, cache)

    def find_path(self,
                  source_lng,
                  source_lat,
                  target_lng,
                  target_lat,
                  params=None):
        """ Find the optimal path with Mapbox Directions HTTP API

        :param float source_lng: longitude value of the starting position
        :param float source_lat: latitude value of the starting position
        :param float target_lng: longitude value of the ending position
        :param float target_lat: latitude value of the ending position
        :param Dict params: the other query parameters for the mapbox router
        :return: None for no path found; a JSON object for the found path info
        """
        self.coordinates = "{0},{1}|{2},{3}".format(source_lng, source_lat,
                                                    target_lng, target_lat)
        self.params = {} if params is None else params
        self.params.update({'api_key': self.api_key})
        self.params.update({'profile': self.profile})
        self.params.update({'coordinates': self.coordinates})

        LOGGER.info("Sending request to Mapbox Directions API server")
        LOGGER.debug("Query string parameters are: %s", str(self.params))
        if self.request_interval > 0:
            sleep(self.request_interval)
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
