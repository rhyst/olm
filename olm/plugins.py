import os
import sys
import imp
from blinker import signal
from olm.logger import get_logger

logger = get_logger('olm.plugins')

class Plugins:
    def __init__(self, context):
        self.receivers = []
        self.load_plugins(context)

    def load_plugins(self, context):
        logger.info('Loading plugins')
        for plugin in context['PLUGINS']:
            logger.debug('Loading plugin %s', plugin)
            sys_path = sys.path
            try:
                path = os.path.join(context.PLUGINS_FOLDER, plugin)
                sys.path.append(path)
                pyfile = os.path.join(path, plugin + '.py')
                py_mod = imp.load_source(plugin, pyfile)
                registrations = getattr(py_mod, 'register')()
                if type(registrations) is tuple:
                    registrations = [ registrations ]
                for registration in registrations:
                    # TODO: Check if valid signal
                    sender = signal(registration[0])
                    receiver = sender.connect(registration[1])
                    self.receivers.append((registration[0], receiver))
                sys.path = sys_path
            except Exception as e:
                sys.path = sys_path
                logger.warn('Plugin %s failed to load.', plugin)
                logger.warn(e)

    def unload_plugins(self):
        for receiver in self.receivers:
            signal(receiver[0]).disconnect(receiver[1])
        