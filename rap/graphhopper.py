"""
Python class file of fetching routes from Graphhopper's Routing API
"""

from rap.base import RoutingService


class GraphHopperRouter(RoutingService):
    """ Wrapper class of Graphhopper routing API v1

    For more details, visit the official documentation page:
    https://graphhopper.com/api/1/docs/routing/
    """
    v1_baseuri = "https://graphhopper.com/api/1/route"

    def __init__(self, key):
        self.key = key

    def find_path(
            self,
            origin_lng, origin_lat,
            dest_lng, dest_lat,
            profile=None,
            params=None):
        pass
