'''
Python class file of fetching routes from Mapbox's Directions API
'''

from mapbox import Directions

POINT_FEATURES_TEMPLATE = [{
    "type": "Feature",
    "properties": {},
    "geometry": {
        "type": "Point",
        "coordinates": [
            -87.33787536621092,
            36.539156961321574]
        }
    }, {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Point",
            "coordinates": [
                -88.2476806640625,
                36.92217534275667]
            }
        }
    ]


class MapBoxRouter:
    def __init__(self, key):
        self.token = key
        self.points = POINT_FEATURES_TEMPLATE

    def find_path(
            self,
            origin_lng, origin_lat, dest_lng, dest_lat,
            profile,
            params=None):
        self.points[0]['geometry']['coordinates'][0] = origin_lng
        self.points[0]['geometry']['coordinates'][1] = origin_lat
        self.points[1]['geometry']['coordinates'][0] = dest_lng
        self.points[1]['geometry']['coordinates'][1] = dest_lat
        self.profile = profile
        self.params = params
        res = Directions(access_token=self.token).directions(
                self.points, params)
        res.status_code
