import json
from unittest import TestCase, main
from rap.ors import OpenRouteServiceRouter


class OpenRouteServiceRouterTestCase(TestCase):

    def setUp(self):
        with open('./routerconf.json') as kf:
            router_conf = json.loads(kf.read())
        self.router = OpenRouteServiceRouter(
            "walking.normal", router_conf['openrouteservice']['key'])

    def test_find_path_for_walking_profile(self):
        origin = {'lng': 11.55, 'lat': 48.18}
        dest = {'lng': 11.62, 'lat': 48.11}
        res = self.router.find_path(origin['lng'], origin['lat'],
                                    dest['lng'], dest['lat'],
                                    {"geometry_format": "geojson"})
        self.assertIsNotNone(res)


if __name__ == "__main__":
    main()
