"""
Usage:
    rapy -r ROUTER -p PROFILE -f LANDMARK -t POINTS [-o OUTPUT_DIR] [-x PARAMS] [-v | --verbose]
    rapy -h | --help
    rapy --version

Fetch optimal routes from the location described in the geojson format file
LANDMARK to all the locations recorded in the POINTS csv file with an
online routing service of ROUTER, write the results in OUTPUT_DIR. The extra
parameters for different routing services can be provided in the json file
specified by the PARAMS argument. The test area information are configured
in `appconf.json` file.

Options:
    -r ROUTER      Set routing service provider (required)
    -p PROFILE     Set the preferred routing profile indicating the
                   transportation mode to use for routing (required)
                   [default: walking]
    -f LANDMARK    Set the source location of the path searching job in a
                   geojson format file, which is usually a landmark within
                   the test area (required)
    -t POINTS      Set the input csv file containing all the points (required)
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
    LANDMARK       Point information file in geojson format. Must be a valid
                   GeoJSON Point `Feature`. It will be used as the
    POINTS         Points information file in csv format. Must have `x`, `y`,
                   and `id` fields at least to record the longtitude and
                   latitude coordinates and id
                   source/origin/starting location of the probing job.
    OUTPUT_DIR     Directory for saving routing results, default to ./output
    PARAMS         JSON file containing extra parameters for the router

Examples:
    rapy -r mapbox -p walking -f ./input/muenchen-hbf.json -t ./input/munich.csv
    rapy -r graphhopper -p driving -f ./input/heidelberg-hbf.json -t ./input/heidelberg.csv -o ./gh_results -v
"""
import json
import geojson
import os
import csv
import datetime
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
        '-f':
        And(lambda f: os.path.isfile(f),
            error="LANDMARK file {0} does not exist".format(raw_args['-f'])),
        '-t': And(
            lambda t: os.path.isfile(t),
            error="POINTS file {0} does not exist".format(raw_args['-t'])),
        Optional(
            '-o', default='./output'): And(
                lambda o: os.path.isdir(o),
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
    # /OUTPUT_DIR_ROOT/ROUTER/PROFILE/YYYY-MM-DD/SOURCE_TARGET.json
    os.makedirs(output_dir, exist_ok=True)
    save_route_to(res,
                  os.path.join(output_dir, '{0}_{1}.json'.format(
                      source['id'], target['id'])))
    return 1


def cal_accessibility(router, source, all_pts, output_dir, params=None):
    print("Calculating the accessibilities from the landmark location {0}...".
          format(str(source['geometry']['coordinates'])))
    s = {
        'id': -1,
        'x': source['geometry']['coordinates'][0],
        'y': source['geometry']['coordinates'][1]
    }
    pt_acc_list = []
    for p in all_pts:
        pt_acc_list.append({
            'id': p['id'],
            'x': p['x'],
            'y': p['y'],
            'acc': try_touching(router, s, p, output_dir, params)
            })

    return pt_acc_list


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
    stub_pts = []
    logger.info("Open input data file with stub points")
    with open(args['-t'], 'r') as f:
        logger.debug("Data file {0} has been opened for reading".format(args[
            '-t']))
        pf = csv.DictReader(f)
        for r in pf:
            logger.debug("Current row in the points info file: {0}".format(
                str(r)))
            stub_pts.append({
                'x': float(r['x']),
                'y': float(r['y']),
                'id': int(r['id'])
            })

    landmark = {}
    logger.info("Open landmark geojson file.")
    with open(args['-f'], 'r') as f:
        landmark = geojson.load(f)

    logger.info("Load extra parameter file for the current router")
    if args['-x'] is None:
        params = None
    else:
        with open(args['-x']) as f:
            params = json.load(f)

    logger.info(
        "Calculate accessibilities for all the stub points from the landmark")
    points_with_accessibility = cal_accessibility(
        router, landmark, stub_pts,
        os.path.join(args['-o'], args['-r'], args['-p'],
                     datetime.date.today().isoformat()), params)
    logger.debug("And we get the points with accessibilities: {0}".format(
        str(points_with_accessibility)))

    with open(os.path.join(args['-o'], '{0}.csv'.format(args['-r'])),
              'w') as f:
        fieldnames = points_with_accessibility[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points_with_accessibility)

    logger.info("All done!")
