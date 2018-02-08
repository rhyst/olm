import os
import sys
import logging
import imp
from blinker import signal

def load_plugins(context):
    for plugin in context['PLUGINS']:
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
                signal_sender = signal(registration[0])
                signal_sender.connect(registration[1])
            sys.path = sys_path
        except Exception as e:
            sys.path = sys_path
            logging.warn('Plugin %s failed to load.', plugin)
            logging.warn(e)
