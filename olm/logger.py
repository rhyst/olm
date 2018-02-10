import logging, verboselogs, coloredlogs

def get_logger(name=''):
    logger = verboselogs.VerboseLogger(name)
    coloredlogs.install(level='INFO', logger=logger, fmt='%(asctime)s [%(name)s] %(message)s')
    return logger