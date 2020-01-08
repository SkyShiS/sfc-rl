import logging


def setup_custom_logger(name):
    # formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    formatter = logging.Formatter(fmt='%(levelname)s -%(processName)s -%(module)s \t - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    # logger.setLevel(logging.INFO)
    logger.setLevel(logging.CRITICAL)
    logger.addHandler(handler)

    # logger switch
    # logger.disabled = True

    return logger


log = setup_custom_logger('root')