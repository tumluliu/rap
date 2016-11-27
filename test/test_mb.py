import unittest
from rap.mb import MapboxRouter


class MapboxRouterTestCase(unittest.TestCase):

    def setUp(self):
        with open('../apikeys.json') as kf:
            apikey_config = kf.read()
        self.router = MapboxRouter(apikey_config['mapbox']['key'])

    def test_find_path_for_walking_profile(self):
        origin = {'lng': 11.55, 'lat': 48.18}
        dest = {'lng': 11.62, 'lat': 48.11}
        params = {'radiuses': '10;10'}
        res = self.router.find_path(
                origin['lng'], origin['lat'],
                dest['lng'], dest['lat'],
                "walking", params)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
