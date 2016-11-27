'''
Usage:
    rap -p PROVIDER -o FILE

Options:
    -p PROVIDER  Specify the direction service provider, can be
                 (mapbox | mapzen | graphhopper | google | here | tomtom)
    -o FILE      Specify the output probing data file
    -h --help    Show this help
    --version    Show version number
'''


def __main__():
    '''
    Entrypoint of command line interface.
    '''
    from docopt import docopt
    arguments = docopt(__doc__, version='0.1.0')
    print(arguments)
