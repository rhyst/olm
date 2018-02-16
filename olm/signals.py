import time
from blinker import signal
from olm.helper import Map
from olm.logger import get_logger

logger = get_logger('olm.signal')

signals = Map({
    'INITIALISED':              "INITIALISED",             # args: context
    'SITE_INITIALISED':         "SITE_INITIALISED",        # args: context
    "BEFORE_MD_CONVERT":        "BEFORE_MD_CONVERT",       # args: context, content      
    'BEFORE_CACHING':           "BEFORE_CACHING",          # args: context, articles
    'AFTER_ARTICLE_READ':       "AFTER_ARTICLE_READ",      # args: context, article
    'AFTER_PAGE_READ':          "AFTER_PAGE_READ",         # args: context, article
    'AFTER_ALL_ARTICLES_READ':  "AFTER_ALL_ARTICLES_READ", # args: context, articles
    'BEFORE_WRITING':           "BEFORE_WRITING",          # args: context
    'BEFORE_ARTICLE_WRITE':     "BEFORE_ARTICLE_WRITE",    # args: context, article
    'AFTER_WRITING':            "AFTER_WRITING"            # args: context, article
})

class Signal:
    def __init__(self, signal_value):
        logger.spam('Instantiating new Signal "%s"', signal_value)
        if signal_value not in signals:
            logger.error('No such signal %s', signal_value)
            raise Exception('No such signal %s', signal_value)
        self.signal_value = signal_value
        self.sender = signal(signal_value)

    def send(self, **kwargs):
        time_start = time.time()
        logger.spam('Sending signal "%s"', self.signal_value)
        self.sender.send(self.signal_value, **kwargs)
        logger.spam('Ran signal "%s" in %.3f seconds', self.signal_value, (time.time() - time_start))

