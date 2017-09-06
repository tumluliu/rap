import json
from unittest import TestCase, main
from rap.google import GoogleMapsRouter


class GoogleMapsRouterTestCase(TestCase):

    def setUp(self):
        with open('./routerconf.json') as kf:
            router_conf = json.loads(kf.read())
        self.router = GoogleMapsRouter(
            "walking", router_conf['google']['key'])

    def test_find_path_for_walking_profile(self):
        origin = {'lng': 11.55, 'lat': 48.18}
        dest = {'lng': 11.62, 'lat': 48.11}
        res = self.router.find_path(origin['lng'], origin['lat'],
                                    dest['lng'], dest['lat'])
        self.assertIsNotNone(res)


if __name__ == "__main__":
    main()
