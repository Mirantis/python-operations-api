import inspect
import logging.config
import logging
import sys
import yaml

from os.path import dirname, exists, join, normpath


class ClassLoggerMixin(object):

    def __init__(self, *args, **kwargs):
        name = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        self.logger = logging.getLogger(name)
        super().__init__(*args, **kwargs)


def setup_logging(debug_mode, path=None):
    default_level = 'INFO'
    full_path = normpath(join(dirname(__file__), '..', path or 'config/logger_config.yml'))

    if exists(full_path):
        with open(full_path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                loggers = config['loggers']
                for logger, value in loggers.items():
                    if debug_mode:
                        loggers[logger]['level'] = 'DEBUG'
                    else:
                        current_level = value.get('level')
                        loggers[logger]['level'] = default_level if not current_level else current_level

                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Failed to load configuration file.\
                      Using default configs. Operations API generic logging, user logging will not work properly')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print('Failed to load configuration file.\
              Using default configs. Operations API generic logging, user logging will not work properly')
