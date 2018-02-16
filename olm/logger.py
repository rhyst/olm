import logging, verboselogs, coloredlogs

LEVEL = None

def set_log_level(level='INFO'):
    global LEVEL
    LEVEL=level

def get_logger(name=''):
    logger = verboselogs.VerboseLogger(name)
    coloredlogs.install(level=LEVEL, logger=logger, fmt='%(asctime)s [%(name)s] %(message)s')
    return logger