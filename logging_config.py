import logging.config


def configure_logging():
    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)

    # Try logging a message to test if the logging is configured correctly
    try:
        logger.info('Logging test message')
    except Exception as e:
        logger.exception('Error while logging test message: %s', e)

    return logger
