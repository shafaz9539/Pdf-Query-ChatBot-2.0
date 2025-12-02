import logging
from enum import Enum, StrEnum

LOG_FORMAT_DEBUG = "%(levelname)s: %(message)s:%(pathname)s:%(funcName)s:%(lineno)d"

class LogLevels(StrEnum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"

def configure_logging(log_level: str = LogLevels.error):
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        logging.basicConfig(level=logging.error)
        return
    
    if log_level == LogLevels.debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT_DEBUG)

    logging.basicConfig(level=log_level)