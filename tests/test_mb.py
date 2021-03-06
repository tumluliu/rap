import json
from unittest import TestCase, main
from rap.mapbox import MapboxRouter


class MapboxRouterTestCase(TestCase):

    def setUp(self):
        with open('./routerconf.json') as kf:
            router_conf = json.loads(kf.read())
        self.router = MapboxRouter("walking", router_conf['mapbox']['key'])

    def test_find_path_for_walking_profile(self):
        origin = {'lng': 11.55, 'lat': 48.18}
        dest = {'lng': 11.62, 'lat': 48.11}
        params = {'radiuses': '100;100'}
        res = self.router.find_path(origin['lng'], origin['lat'],
                                    dest['lng'], dest['lat'],
                                    params)
        self.assertIsNotNone(res)


if __name__ == "__main__":
    main()
