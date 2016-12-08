"""Python class file of fetching routes from Mapbox's Directions API
"""

from uritemplate import URITemplate
from .base import RoutingService


class MapboxRouter(
        RoutingService
):
    """ Wrapper class of Mapbox direction http API v5

    The mapbox-sdk-py is not used because it's out of date
    and lacks maintenance.
    For more details, visit the official documentation page:
    https://www.mapbox.com/api-documentation/?language=cURL#directions

    Sample request URL:
    https://api.mapbox.com/directions/v5/mapbox/cycling/-122.42,37.78;-77.03,38.91?access_token=your-access-token
    https://api.mapbox.com/directions/v5/mapbox/driving/13.4301,52.5109;13.4265,52.5080;13.4194,52.5072?radiuses=40;;100&geometries=polyline&access_token=your-access-token
    """

    v5_baseuri = "https://api.mapbox.com/directions/v5"
    api_uri_template = URITemplate(
        v5_baseuri
        +
        "{/profile}{/coordinates}"
    )
    profile_dict = {
        "driving":
        "mapbox/driving",
        "walking":
        "mapbox/walking",
        "cycling":
        "mapbox/cycling"
    }

    def __init__(
            self,
            api_key,
            profile,
            cache=None
    ):
        self.token = api_key
        if profile not in self.profile_dict.keys(
        ):
            # The profile passed in is not supported by Mapbox routing service
            return None
        self.profile = self.profile_dict[
            profile]
        super(
        ).__init__(
            self,
            api_key,
            cache
        )

    def find_path(
            self,
            source_lng,
            source_lat,
            target_lng,
            target_lat,
            params=None
    ):
        """ Find the optimal path with Mapbox Directions HTTP API

        :param source_lng: longitude value of the starting position
        :param source_lat: latitude value of the starting position
        :param target_lng: longitude value of the ending position
        :param target_lat: latitude value of the ending position
        :param params: the other query parameters for the mapbox router
        """
        self.coordinates = "{0},{1};{2},{3}".format(
            source_lng,
            source_lat,
            target_lng,
            target_lat
        )
        self.params = params

        # TODO(lliu): fetch the routes via mapbox direction api calling
        uri = self.api_uri_template.expand({
            'profile':
            self.
            profile,
            'coordinates':
            self.
            coordinates
        })
        # query_str = URIVariable('?' + ','.join(self.params.keys()))
        # query_str.expand(self.params)
        # uri += query_str
        resp = self.session.get(
            uri,
            params=params
        )
        self.handle_http_error(
            resp
        )
        resp.geojson = resp.json
        return resp
