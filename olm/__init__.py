import sys
import os
import time

from olm.context import load_context, load_default_context
from olm.plugins import Plugins
from olm.signals import Signal, signals
from olm.logger import get_logger
from olm.website import Site

logger = get_logger('olm')

def main():
    if len(sys.argv) < 2:
        print("Please identify the source folder")
        return

    time_all = time.time()
    """Main olm function"""
    logger.notice("Beginning static site generation")

    CONTEXT = load_default_context(sys.argv[1])

    settings_file_path = os.path.abspath(os.path.join(sys.argv[1], 'settings.py'))
    if os.path.isfile(settings_file_path):
        CONTEXT = load_context(CONTEXT, settings_file_path=settings_file_path)

    plugins = Plugins(CONTEXT)

    signal_sender = Signal(signals.INITIALISED)
    signal_sender.send(context=CONTEXT)

    site = Site(CONTEXT)
    site.build_site()

    subsites = site.subsites

    base_folder = CONTEXT.BASE_FOLDER
    source_folder = CONTEXT.SOURCE_FOLDER
    for subsite in subsites:
        plugins.unload_plugins()
        subsite_name = subsite[1:]
        logger.info("Found subsite '%s'", subsite_name)
        if subsite_name in CONTEXT.SUBSITES:
            subsite_context = load_context(CONTEXT, settings=CONTEXT.SUBSITES[subsite_name])
        else:
            subsite_context = CONTEXT
        plugins.load_plugins(subsite_context)
        subsite_context.OUTPUT_FOLDER = os.path.abspath(os.path.join(base_folder, 'dist', subsite_name))
        subsite_context.BASE_FOLDER = os.path.join(source_folder, subsite)
        subsite_context.SOURCE_FOLDER = os.path.join(source_folder, subsite)
        site = Site(subsite_context)
        site.build_site()

    logger.success("Completed everything in %.3f seconds", (time.time() - time_all))

if __name__== "__main__":
  main()