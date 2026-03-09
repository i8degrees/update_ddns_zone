
import os
import logging

def _filter_warn(level):
    level = getattr(logging, level)

    def filter(record):
        return record.levelno <= level

    return filter

LOG_CONFIG_PATH = 'config/log.ini'
config: dict|str|None = None

if os.path.isfile(LOG_CONFIG_PATH) and os.access(LOG_CONFIG_PATH, os.R_OK):
    from logging.config import fileConfig

    #log.debug(f'Initializing logging with configuration at {LOG_CONFIG_PATH}')
    print(f'Initializing logging with configuration at {LOG_CONFIG_PATH}')
    config = fileConfig(fname=LOG_CONFIG_PATH)
else:
    #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    from logging.config import dictConfig

    default_config = dict(
        version = 1,
        disable_existing_loggers = False,
        formatters = {
            'simple': {
                'format': '%(name)s [%(levelname)-4s] - %(message)s'
            },
        },
        #filters = {
            #'warnings_and_below': {
                #'()' : '__main__._filter_warn',
                #'level': 'WARNING'
            #},
        #},
        handlers = {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
                #'filters': ['warnings_and_below'],
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'simple',
                'stream': 'ext://sys.stderr',
            },

            # ?? Enable the following when env["LOG_FILE"] is set
            #'file': {
                #'class': 'logging.FileHandler',
                #'formatter': 'simple',
                #'filename': 'app.log',
                #'mode': 'w',
            #},
        },
        root = {
            'level': logging.INFO,
            'handlers': ['stdout', 'stderr'],
            #'handlers': ['stdout', 'stderr', 'file'],
        },
    )

    # ?? This will never be printed with the default configuration parameters;
    # ?? I am leaving this as-is until we figure out where exactly we intend
    # ?? on storing dotenv environment init.
    #log.debug("Initializing logging with the default configuration")
    logging.config.dictConfig(default_config)
