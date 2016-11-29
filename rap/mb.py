"""
Python class file of fetching routes from Mapbox's Directions API
"""

from uritemplate import URITemplate
from rap.base import RoutingService


class MapboxRouter(RoutingService):
    """ Wrapper class of Mapbox direction http API v5

    The mapbox-sdk-py is not used because it's out of date
    and lacks maintenance.
    For more details, visit the official documentation page:
    https://www.mapbox.com/api-documentation/?language=cURL#directions
    """
    v5_baseuri = "https://api.mapbox.com/directions/v5{/profile}{/coordinates}"
    valid_profiles = {
        "driving": "mapbox/driving",
        "walking": "mapbox/walking",
        "cycling": "mapbox/cycling"
    }

    def __init__(self, key):
        self.token = key

    def find_path(self,
                  source_lng,
                  source_lat,
                  target_lng,
                  target_lat,
                  profile="walking",
                  params=None):
        """ Find the optimal path with Mapbox Directions HTTP API

        :param source_lng: longitude value of the starting position
        :param source_lat: latitude value of the starting position
        :param target_lng: longitude value of the ending position
        :param target_lat: latitude value of the ending position
        :param profile: name of a transportation mode/profile
        :param params: the other query parameters for the mapbox router
        """
        self.coordinates = "{0},{1};{2},{3}".format(source_lng, source_lat,
                                                    target_lng, target_lat)
        self.profile = profile
        self.params = params

        # TODO(lliu): fetch the routes via mapbox direction api calling
        res = None
        return res
