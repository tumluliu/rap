# rap

routers as probes

`rap` is the library, and `rapy` is the command-line tool

```
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
```
