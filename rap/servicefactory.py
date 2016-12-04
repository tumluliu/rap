""" Factory of RoutingService classes """

import json
from .mb import MapboxRouter
from .graphhopper import GraphHopperRouter

# from . import mapzen
# from . import google
# from . import here
# from . import tomtom
""" Factory method of creating concrete routing service instances
"""
VALID_ROUTING_SERVICES = [
    'mapbox', 'graphhopper', 'mapzen', 'google', 'here', 'tomtom'
]


def RoutingServiceFactory(service_name):
    if service_name not in VALID_ROUTING_SERVICES:
        # TODO(lliu): Here should throw an exception or deal with it in an
        # identical way
        return None
    with open('../apikeys.json', 'r') as f:
        service_provider_conf = json.load(f)

    # TODO(lliu): The following stuff of course should be prettified
    # ATTENTION!! A pile of ugly things are coming...
    if service_name == 'mapbox':
        return MapboxRouter(service_provider_conf['mapbox']['key'])
    elif service_name == 'graphhopper':
        return GraphHopperRouter(service_provider_conf['graphhopper']['key'])
