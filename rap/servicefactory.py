"""Factory of RoutingService classes
"""

import json
import logging
from .mapbox import MapboxRouter
from .graphhopper import GraphHopperRouter

# from . import mapzen
# from . import google
# from . import here
# from . import tomtom

logger = logging.getLogger(__name__)


def RoutingServiceFactory(service_name, profile):
    logger.debug("Create concrete router for {0} with profile {1}".format(
        service_name, profile))
    with open('routerconf.json', 'r') as f:
        service_provider_conf = json.load(f)
    # TODO(lliu): The following stuff of course should be prettified
    # ATTENTION!! A pile of ugly things are coming...
    if service_name == 'mapbox':
        logger.info("Create mapbox router")
        return MapboxRouter(profile, service_provider_conf['mapbox']['key'])
    elif service_name == 'graphhopper':
        logger.info("Create graphhopper router")
        return GraphHopperRouter(profile,
                                 service_provider_conf['graphhopper']['key'])
