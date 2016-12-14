"""
Usage:
    rapy -r ROUTER -p PROFILE -i INPUT_FILE [-o OUTPUT_DIR] [-x PARAMS] [-v | --verbose]
    rapy -h | --help
    rapy --version

Fetch optimal routes between every two locations in the INPUT_FILE csv file
with an online routing service of ROUTER, write the results in OUTPUT_DIR.
The extra parameters for different routing services can be provided in the
JSON file specified by the PARAMS argument.  The test area information are
configured in appconf.json file.

Options:
    -r ROUTER      Set routing service provider (required)
    -p PROFILE     Set the preferred routing profile indicating the
                   transportation mode to use for routing (required)
                   [default: walking]
    -i INPUT_FILE  Set the input csv file containing all the points (required)
    -o OUTPUT_DIR  Set the directory for saving routing results, create a new
                   directory if not exists (optional) [default: ./output]
    -x PARAMS      Extra parameters for the router, a plain text file in JSON
                   format (optional)
    -v --verbose   Show running log in detail
    -h --help      Show this help
    --version      Show version number

Arguments:
    ROUTER         Routing service API provider name. The valid values are
                   configured in appconf.json file
    PROFILE        Routing profile name indicating what kind of transportation
                   mode should be use, default to walking
    INPUT_FILE     Points information file in csv format. Must have `x`, `y`,
                   and `id` fields at least to record the longtitude and
                   latitude coordinates and id
    OUTPUT_DIR     Directory for saving routing results, default to ./output
    PARAMS         JSON file containing extra parameters for the router

Examples:
    rapy -r mapbox -p walking -i ./input/munich.csv
    rapy -r graphhopper -p driving -i ./input/heidelberg.csv -o ./gh_results -v
"""
import json
import os
import csv
from functools import reduce
import logging.config
import logging
from docopt import docopt, DocoptExit
try:
    from schema import Schema, And, Or, Optional, Use, SchemaError
except ImportError:
    exit('This example requires that `schema` data-validation library'
         ' is installed: \n    pip install schema\n'
         'https://github.com/halst/schema')
from rap import __version__, RoutingServiceFactory

LOGGING_CONF_FILE = 'logging.json'
DEFAULT_LOGGING_LVL = logging.WARNING
path = LOGGING_CONF_FILE
value = os.getenv('RAPY_LOG_CFG', None)
if value:
    path = value
if os.path.exists(path):
    with open(path, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
else:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_arguments(raw_args, conf):
    logger.info("Validating input arguments")
    sch = Schema({
        '-r': And(Use(str.lower),
                  lambda r: str.lower(r) in conf['routers'],
                  error="ROUTER should be one of {0}".format(', '.join(conf[
                      'routers']))),
        '-p': And(Use(str.lower),
                  lambda p: str.lower(p) in conf['profiles'],
                  error="PROFILE should be one of {0}".format(', '.join(conf[
                      'profiles']))),
        '-i': And(lambda i: os.path.isfile(i),
                  error="File {0} does not exist".format(raw_args['-i'])),
        Optional(
            '-o', default='./output'):
        And(lambda o: os.path.isdir(o),
            error="{0} is not a valid directory".format(raw_args['-o'])),
        Optional('-x'): Or(
            None,
            lambda x: os.path.isfile(x),
            error="Parameters file {0} does not exist".format(raw_args['-x'])),
        Optional('--help'): Or(True, False),
        Optional('--version'): Or(True, False),
        Optional('--verbose'): Or(True, False)
    })
    try:
        args = sch.validate(raw_args)
    except DocoptExit as e:
        logger.error("Parse command-line arguments failed!")
        print(e.message)
    except SchemaError as e:
        logger.error("Validate command-line arguments failed!")
        print(e.autos)
        exit(e)
    return args


def save_route_to(route, filepath):
    logger.debug("Save the found route information to {0} ".format(filepath))
    with open(filepath, 'w') as f:
        json.dump(route, f)


def try_touching(router, source, target, output_dir, params=None):
    logger.debug("Try searching for a path from {0} to {1}".format(
        str(source), str(target)))
    res = router.find_path(source['x'], source['y'], target['x'], target['y'],
                           params)
    if res is None:
        return 0
    # The found routes will be stored in a directory like
    # /OUTPUT_DIR_ROOT/ROUTER/PROFILE/SOURCE_TARGET.json
    os.makedirs(output_dir, exist_ok=True)
    save_route_to(res,
                  os.path.join(output_dir, '{0}_{1}.json'.format(
                      source['id'], target['id'])))
    return 1


def cal_accessibility(router, target, all_pts, output_dir, params=None):
    logger.debug("Calculating the accessibilities of point {0}...".format(
        str(target)))
    i = all_pts.index(target)
    # Put all the points except the target into other_pts list
    other_pts = all_pts[:i] + all_pts[(i + 1):]
    # Calculate how many points can reach the target, and use this value as the
    # target's accessibility index
    p_accessibility = {k: v for k, v in target.items()}
    p_accessibility.update({
        'accessibility': reduce(
            lambda x, y: x + y,
            map(lambda p: try_touching(router, p, target, output_dir, params),
                other_pts), 0)
    })
    return p_accessibility


def main():
    """Entrypoint of command line interface.
    """
    args = docopt(__doc__, version=__version__)
    if args['--verbose']:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info(
            "==== Routers As Probes pYthon command-line tool (rapy) ====")
        logger.info("== Running in verbose mode with DEBUG info ==")
        logger.info("Project page: http://github.com/tumluliu/rap")
        logger.info("Contact: Lu Liu via nudtlliu@gmail.com")
        logger.info("Start working...")
        logger.debug("Arguments for rapy: {0}".format(str(args)))
    else:
        logging.getLogger().setLevel(logging.WARNING)
    with open('appconf.json', 'r') as f:
        appconf = json.load(f)
    args = validate_arguments(args, appconf)
    logger.debug("Arguments after validation: {0}".format(args))
    router = RoutingServiceFactory(args['-r'], args['-p'])
    logger.debug("Router {0} instance has been created".format(
        router.__class__.__name__))
    points = []
    logger.info("Open input data file with stub points")
    with open(args['-i'], 'r') as f:
        logger.debug("Data file {0} has been opened for reading".format(args[
            '-i']))
        pf = csv.DictReader(f)
        for r in pf:
            logger.debug("Current row in the points info file: {0}".format(
                str(r)))
            points.append({
                'x': float(r['x']),
                'y': float(r['y']),
                'id': int(r['id'])
            })

    logger.info("Load extra parameter file for the current router")
    if args['-x'] is None:
        params = None
    else:
        with open(args['-x']) as f:
            params = json.load(f)

    logger.info("Calculate accessibilities for all the stub points")
    points_with_accessibility = list(
        map(lambda p: cal_accessibility(
                router, p, points,
                os.path.join(
                    args['-o'], args['-r'], args['-p']),
                params),
            points))
    logger.debug("And we get the points with accessibilities: {0}".format(
        str(points_with_accessibility)))

    with open(os.path.join(args['-o'], '{0}.csv'.format(args['-r'])),
              'w') as f:
        fieldnames = points_with_accessibility[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points_with_accessibility)

    logger.info("All done!")
