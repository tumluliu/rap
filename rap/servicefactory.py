"""Factory of RoutingService classes
"""

import json
import logging
from .mapbox import MapboxRouter
from .ors import OpenRouteServiceRouter
from .google import GoogleMapsRouter

LOGGER = logging.getLogger(__name__)


def RoutingServiceFactory(service_name, profile):
    """ Factary method for creating concrete router instance
    """
    LOGGER.debug("Create concrete router for %s with profile %s",
                 service_name, profile)
    with open('routerconf.json', 'r') as f:
        service_provider_conf = json.load(f)
    # TODO(lliu): The following stuff of course should be prettified
    # ATTENTION!! A pile of ugly things are coming...
    if service_name == 'mapbox':
        LOGGER.info("Create mapbox router")
        return MapboxRouter(profile,
                            service_provider_conf['mapbox']['key'],
                            service_provider_conf['mapbox']['rate_limit'])
    elif service_name == 'openrouteservice':
        LOGGER.info("Create openrouteservice router")
        return OpenRouteServiceRouter(profile,
                                      service_provider_conf['openrouteservice']['key'],
                                      service_provider_conf['openrouteservice']['rate_limit'])
    elif service_name == 'google':
        LOGGER.info("Create google maps router")
        return GoogleMapsRouter(profile,
                                service_provider_conf['google']['key'],
                                service_provider_conf['google']['rate_limit'])
