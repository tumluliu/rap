"""Factory of RoutingService classes
"""

import json
from .mapbox import MapboxRouter
from .graphhopper import GraphHopperRouter

# from . import mapzen
# from . import google
# from . import here
# from . import tomtom
""" Factory method of creating concrete routing service instances
"""


def RoutingServiceFactory(service_name, profile):
    with open('routerconf.json', 'r') as f:
        service_provider_conf = json.load(f)
    # TODO(lliu): The following stuff of course should be prettified
    # ATTENTION!! A pile of ugly things are coming...
    if service_name == 'mapbox':
        return MapboxRouter(service_provider_conf['mapbox']['key'], profile)
    elif service_name == 'graphhopper':
        return GraphHopperRouter(service_provider_conf['graphhopper']['key'],
                                 profile)
