"""
Usage:
    rap -p PROVIDER -i INPUT_FILE [-o OUTPUT_DIR] [-v | --verbose]
    rap -h | --help
    rap --version

Fetch optimal routes between every two locations in the INPUT_FILE csv file
with an online routing service of PROVIDER, write the results in OUTPUT_DIR.
The test area information are configured in appconf.json file.

Options:
    -p PROVIDER    Set routing service provider (required)
    -i INPUT_FILE  Set the input csv file containing all the points (required)
    -o OUTPUT_DIR  Set the directory for saving routing results, create a new
                   directory if not exists (optional) [default: ./output]
    -v --verbose   Show running log in detail
    -h --help      Show this help
    --version      Show version number

Arguments:
    PROVIDER       Routing service API provider name. The valid values are
                   configured in routerconf.json file
    INPUT_FILE     Points information file in csv format. Must have X, Y and id
                   fields at least to record the longtitude and latitude
                   coordinates and id
    OUTPUT_DIR     Directory for saving routing results, default to ./output

Examples:
    rap -p mapbox
    rap -p graphhopper -o ./gh_results -v
"""
import json
import os
import csv
from docopt import docopt
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


def validate_arguments(raw_args, conf):
    sch = Schema({
        'PROVIDER': And(str,
                        Use(str.lower),
                        lambda p: p in conf.keys(),
                        error='PROVIDER should be one of {0}'.format(', '.join(
                            list(conf.keys())))),
        'INPUT_FILE': Use(os.file.exists,
                          error='Input data file {0} does not exist'.format(
                              raw_args['INPUT_FILE'])),
        'OUTPUT_DIR': Use(os.path.isdir,
                          error='{0} is not a valid directory'.format(raw_args[
                              'OUTPUT_DIR'])),
    })
    try:
        args = sch.validate(raw_args)
    except docopt.DocoptExit as e:
        print(e.message)
    except SchemaError as e:
        print(e.message)
        exit(e)
    return args


def try_touching(router, source, target, profile):
    res = router.find_path(source['x'], source['y'], target['x'], target['y'],
                           profile, None)
    if res is None:
        return 0
    return 1


def cal_accessibility(router, target, all_pts, profile='walking'):
    i = all_pts.index(target)
    other_pts = all_pts[:i] + all_pts[(i + 1):]
    return reduce(
        lambda x, y: x + y,
        map(lambda p: try_touching(router, p, target, profile), other_pts), 0)


def __main__():
    """
    Entrypoint of command line interface.
    """
    args = docopt(__doc__, version=__version__)
    with open('routerconf.json', 'r') as f:
        routerconf = json.load(f)
    args = validate_arguments(args, routerconf)
    print(args)
    router = RoutingServiceFactory(args['PROVIDER'])
    points = []
    with open(args['INPUT_FILE'], 'r') as f:
        pf = csv.DictReader(f)
        for r in pf:
            points.append({
                'x': float(r['X']),
                'y': float(r['Y']),
                'id': int(r['id'])
            })
    points_with_accessibility = list(map(
        lambda p: cal_accessibility(router, p, points, profile='walking'),
        points))
    with open(
            os.path.join(args['OUTPUT_DIR'],
                         '{0}.csv'.format(args['PROVIDER'])), 'w') as f:
        fieldnames = points_with_accessibility[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points_with_accessibility)
