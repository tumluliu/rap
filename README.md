# rap

routers as probes

`rap` is the library, and `rapy` is the command-line tool

## Usage

Please add your own API keys in `routerconf.json` before using this tool.

```
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
```

## Dependencies

- CacheControl==0.11.7
- docopt==0.6.2
- geojson==1.3.3
- requests==2.12.1
- schema==0.6.5
- setuptools==29.0.0
- uritemplate==3.0.0

# Acknowledgements

Thanks for the support of National Natural Science Foundation of China (NSFC) project "Data model and algorithms in socially-enabled multimodal route planning service" (No. 41301431) of which I am the project leader.
