import sys
import os
import time
import argparse

from olm.context import load_context, load_default_context
from olm.plugins import Plugins
from olm.signals import Signal, signals
from olm.logger import get_logger
from olm.website import Site

logger = get_logger('olm')

def main():
    parser = argparse.ArgumentParser(description='Olm static site generator',)
    parser.add_argument('src', action="store", help='Path to site folder')
    parser.add_argument('-s', '--settings', action="store", default=None, help='Path to settings.py file')
    parser.add_argument('-d', '--disable-caching', action="store_true", help='Disable caching')
    args = parser.parse_args()
    if len(sys.argv) < 2:
        logger.warn("Olm requires the path to the site folder")
        logger.warn("\tolm ./path/to/my/site/")
        return

    time_all = time.time()
    """Main olm function"""
    logger.notice("Beginning static site generation")

    CONTEXT = load_default_context(args.src)
    CONTEXT.caching_enabled = True
    if args.disable_caching:
        CONTEXT.caching_enabled = False

    if args.settings is not None:
        settings_file_path = os.path.abspath(args.settings)
    else:
        settings_file_path = os.path.abspath(os.path.join(args.src, 'settings.py'))
    if os.path.isfile(settings_file_path):
        CONTEXT = load_context(CONTEXT, settings_file_path=settings_file_path)
    else:
        logger.error('No valid settings.py file found')
        sys.exit()

    plugins = Plugins(CONTEXT)

    signal_sender = Signal(signals.INITIALISED)
    signal_sender.send(context=CONTEXT)

    site = Site(CONTEXT)
    site.build_site()

    subsites = site.subsites

    base_folder   = CONTEXT.BASE_FOLDER
    output_folder = CONTEXT.OUTPUT_FOLDER
    source_folder = CONTEXT.SOURCE_FOLDER
    for subsite in subsites:
        plugins.unload_plugins()
        subsite_name = subsite[1:]
        logger.info("")
        logger.info("Found subsite '%s'", subsite_name)
        if subsite_name in CONTEXT.SUBSITES:
            subsite_context = load_context(CONTEXT, settings=CONTEXT.SUBSITES[subsite_name])
        else:
            subsite_context = CONTEXT
        plugins.load_plugins(subsite_context)
        subsite_context.OUTPUT_FOLDER  = os.path.abspath(os.path.join(output_folder, subsite_name))
        subsite_context.BASE_FOLDER    = os.path.join(source_folder, subsite)
        subsite_context.SOURCE_FOLDER  = os.path.join(source_folder, subsite)
        subsite_context.CACHE_LOCATION = base_folder + os.sep + 'cache_' + subsite_name + '.pickle'
        site = Site(subsite_context)
        site.build_site()

    logger.success("Completed everything in %.3f seconds", (time.time() - time_all))

if __name__== "__main__":
  main()