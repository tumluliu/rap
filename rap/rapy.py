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
from docopt import docopt
try:
    from schema import Schema, And, Or, Use, SchemaError
except ImportError:
    exit('This example requires that `schema` data-validation library'
         ' is installed: \n    pip install schema\n'
         'https://github.com/halst/schema')
from rap import __version__, RoutingServiceFactory


def validate_arguments(raw_args, conf):
    sch = Schema({
        'ROUTER': And(str,
                      Use(str.lower),
                      lambda r: r in conf['routers'],
                      error='ROUTER should be one of {0}'.format(', '.join(
                          conf['routers']))),
        'PROFILE': And(str,
                       Use(str.lower),
                       lambda p: p in conf['profiles'],
                       error='PROFILE should be one of {0}'.format(', '.join(
                           conf['profiles']))),
        'INPUT_FILE': Use(os.file.exists,
                          error='Input data file {0} does not exist'.format(
                              raw_args['INPUT_FILE'])),
        'OUTPUT_DIR': Use(os.path.isdir,
                          error='{0} is not a valid directory'.format(raw_args[
                              'OUTPUT_DIR'])),
        'PARAMS': Or(None,
                     Use(os.file.exists,
                         error='Can not find extra parameters file {0}'.format(
                             raw_args['PARAMS'])))
    })
    try:
        args = sch.validate(raw_args)
    except docopt.DocoptExit as e:
        print(e.message)
    except SchemaError as e:
        print(e.message)
        exit(e)
    return args


def save_route_to(route, filepath):
    with open(filepath, 'w') as f:
        json.dump(route, f)


def try_touching(router, source, target, output_dir, params=None):
    res = router.find_path(source['x'], source['y'], target['x'], target['y'],
                           params)
    if res is None:
        return 0
    # The found routes will be stored in the form that looks like
    # /OUTPUT_DIR_ROOT/ROUTER/PROFILE/SOURCE_TARGET.json
    os.makedirs(output_dir, exist_ok=True)
    save_route_to(res.geojson,
                  os.path.join(output_dir, '{0}_{1}.json'.format(
                      source['id'], target['id'])))
    return 1


def cal_accessibility(router, target, all_pts, output_dir, params=None):
    i = all_pts.index(target)
    # Put all the points except the target into other_pts list
    other_pts = all_pts[:i] + all_pts[(i + 1):]
    # Calculate how many points can reach the target, and use this value as the
    # target's accessibility index
    return reduce(
        lambda x, y: x + y,
        map(lambda p: try_touching(router, p, target, output_dir, params),
            other_pts), 0)


def main():
    """Entrypoint of command line interface.
    """
    args = docopt(__doc__, version=__version__)
    with open('appconf.json', 'r') as f:
        appconf = json.load(f)
    args = validate_arguments(args, appconf)
    print(args)
    router = RoutingServiceFactory(args['ROUTER'], args['PROFILE'])
    points = []
    with open(args['INPUT_FILE'], 'r') as f:
        pf = csv.DictReader(f)
        for r in pf:
            points.append({
                'x': float(r['x']),
                'y': float(r['y']),
                'id': int(r['id'])
            })

    if args['PARAMS'] is None:
        params = None
    else:
        with open(args['PARAMS']) as f:
            params = json.load(f)

    points_with_accessibility = list(
        map(lambda p: cal_accessibility(
                router, p, points, args['PROFILE'],
                os.path.join(
                    args['OUTPUT_DIR'], args['ROUTER'], args['PROFILE']),
                params),
            points))

    with open(
            os.path.join(args['OUTPUT_DIR'], '{0}.csv'.format(args['ROUTER'])),
            'w') as f:
        fieldnames = points_with_accessibility[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points_with_accessibility)
