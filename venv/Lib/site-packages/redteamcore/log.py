import logging
import sys

ALLOWED_LOGGING_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


class StdErrFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.ERROR, logging.WARNING, logging.CRITICAL)

class StdOutFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)

def set_logging_level(level):
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)
    logger = logging.getLogger('console')
    logger.setLevel(numeric_level)

def console_logger():

    format_string = '%(levelname)s - %(asctime)s - %(message)s'
    logger = logging.getLogger('console')

    formatter = logging.Formatter(fmt=format_string)

    if len(logger.handlers) < 2:
        logger.handlers = []
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        stdout_handler.addFilter(StdOutFilter())
        logger.addHandler(stdout_handler)
        logger.debug("Added stdout logging handler.")

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr_handler.addFilter(StdErrFilter())
        logger.addHandler(stderr_handler)
        logger.debug("Added stderr logging handler.")

    return logger

def info(msg, *args, **kwargs):
    console_logger().info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    console_logger().debug(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    console_logger().warning(msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    console_logger().warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    console_logger().error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    console_logger().critical(msg, *args, **kwargs)
