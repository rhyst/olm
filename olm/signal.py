from blinker import signal
from helper import Map
import logging, verboselogs, coloredlogs 

logger = verboselogs.VerboseLogger('olm.signal')
coloredlogs.install(level='INFO', logger=logger, fmt='%(asctime)s [%(name)s] %(message)s')

signals = Map({
    'INITIALISED':              "INITIALISED",             # args: context
    'AFTER_ARTICLE_READ':       "AFTER_ARTICLE_READ",      # args: context, article
    'AFTER_PAGE_READ':          "AFTER_PAGE_READ",         # args: context, article
    'AFTER_ALL_ARTICLES_READ':  "AFTER_ALL_ARTICLES_READ", # args: context, articles
    'BEFORE_WRITING':           "BEFORE_WRITING",          # args: context
    'BEFORE_ARTICLE_WRITE':     "BEFORE_ARTICLE_WRITE"     # args: context, article
})

class Signal:
    def __init__(self, signal_value):
        logger.debug('Instantiating new Signal "%s"', signal_value)
        if signal_value not in signals:
            logger.error('No such signal %s', signal_value)
            raise Exception('No such signal %s', signal_value)
        self.signal_value = signal_value
        self.sender = signal(signal_value)

    def send(self, **kwargs):
        logger.debug('Sending signal "%s"', self.signal_value)
        self.sender.send(self.signal_value, logger=logger, **kwargs)

