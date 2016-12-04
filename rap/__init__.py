"""
Usage:
    rap -p PROVIDER [-o DIRECTORY] [-v | --verbose]
    rap -h | --help
    rap --version

Fetch optimal routes from the PROVIDER online routing service API, write the
results in DIRECTORY. The input and test area information are configured in
appconf.json file.

Options:
    -p PROVIDER   Set routing service provider (required)
    -o DIRECTORY  Set the directory for saving routing results, create a new
                  directory if not exists (optional) [default: ./]
    -v --verbose  Show running log in detail
    -h --help     Show this help
    --version     Show version number

Arguments:
    PROVIDER      Routing service API provider name. The valid values are
                  configured in routerconf.json file
    DIRECTORY     Directory for saving routing results

Examples:
    rap -p mapbox
    rap -p graphhopper -o ./gh_results -v
"""
from docopt import docopt
import json
import os
try:
    from schema import Schema, And, Use, SchemaError
except ImportError:
    exit('This example requires that `schema` data-validation library'
         ' is installed: \n    pip install schema\n'
         'https://github.com/halst/schema')
from .servicefactory import RoutingServiceFactory

__title__ = 'rap'
__version__ = '0.1.0'
__author__ = 'LIU Lu'
__contact__ = 'nudtlliu@gmail.com'
__license__ = 'MIT'
__all__ = [
    'base', 'servicefactory', 'mb', 'graphhopper', 'mapzen', 'google', 'here',
    'tomtom'
]


def __main__():
    """
    Entrypoint of command line interface.
    """
    args = docopt(__doc__, version=__version__)
    with open('routerconf.json', 'r') as f:
        routerconf = json.load(f)
    sch = Schema({
        'DIRECTORY':
        Use(os.path.isdir,
            error='{0} is not a valid directory'.format(args['DIRECTORY'])),
        'PROVIDER': And(str,
                        Use(str.lower),
                        lambda p: p in routerconf.keys(),
                        error='PROVIDER should be one of {0}'.format(', '.join(
                            list(routerconf.keys()))))
    })
    try:
        args = sch.validate(args)
        router = RoutingServiceFactory(args['PROVIDER'])
        router.find_path(0, 0, 0, 0)
    except docopt.DocoptExit as e:
        print e.message
    except SchemaError as e:
        print e.message
        exit(e)
    print(args)
