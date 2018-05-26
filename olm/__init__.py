import sys
import os
import time
import argparse
import locale

parser = argparse.ArgumentParser(description='Olm static site generator',)
parser.add_argument('src', action="store", help='Path to site folder')
parser.add_argument('-i', '--init', action="store_true", help='Initiliase a project at src')
parser.add_argument('-d', '--disable-caching', action="store_true", help='Disable caching')
parser.add_argument('-r', '--disable-caching-and-rewrite', action="store_true", help='Disable caching but still rewrite cache files')
parser.add_argument('-s', '--settings', action="store", default=None, help='Path to settings.py file')
parser.add_argument('-l', '--log-level', action="store", default="NOTICE", help='Set log level')
args = parser.parse_args()

from olm.logger import get_logger, set_log_level
set_log_level(args.log_level)

# Imports here in order to get correct log level
from olm.context import load_context, load_context_from_file, load_default_context
from olm.plugins import Plugins
from olm.signals import Signal, signals
from olm.website import Site
from olm.quickstart import quickstart

logger = get_logger('olm')

def main():
    """Main olm function"""
    if args.init:
        logger.notice("Setting up basic website")
        base_path = os.path.abspath(args.src)
        if os.listdir(base_path):
            logger.error("The directory must be empty in order to initialise")
            return
        quickstart(base_path)
        logger.success("Done! Run 'olm {}'".format(args.src))
        return

    time_all = time.time()
    logger.notice("Beginning static site generation")

    if args.settings is not None:
        settings_file_path = os.path.abspath(args.settings)
    else:
        settings_file_path = os.path.abspath(os.path.join(args.src, 'settings.py'))
    if os.path.isfile(settings_file_path):
        CONTEXT = load_context_from_file(settings_file_path, load_default_context(args.src))
    else:
        logger.error('No valid settings.py file found')
        sys.exit()
    
    CONTEXT.caching_enabled = True
    CONTEXT.rewrite_cache_files_when_disabled = False
    if args.disable_caching or args.disable_caching_and_rewrite:
        CONTEXT.caching_enabled = False
    if args.disable_caching_and_rewrite:
        CONTEXT.rewrite_cache_files_when_disabled = True

    if 'LOCALE' in CONTEXT:
        logger.debug("Setting locale to %s", CONTEXT.LOCALE)
        locale.setlocale(locale.LC_ALL,CONTEXT.LOCALE)

    plugins = Plugins(CONTEXT)

    signal_sender = Signal(signals.INITIALISED)
    signal_sender.send(context=CONTEXT)

    site = Site(CONTEXT)
    site.build_site()

    subsites = site.subsites

    for subsite in subsites:
        CONTEXT = load_context_from_file(settings_file_path, load_default_context(args.src))
        CONTEXT.caching_enabled = True
        CONTEXT.rewrite_cache_files_when_disabled = False
        if args.disable_caching or args.disable_caching_and_rewrite:
            CONTEXT.caching_enabled = False
        if args.disable_caching_and_rewrite:
            CONTEXT.rewrite_cache_files_when_disabled = True
        plugins.unload_plugins()
        subsite_name = subsite[1:]
        logger.info("")
        logger.info("Found subsite '%s'", subsite_name)
        if subsite_name in CONTEXT.SUBSITES:
            subsite_context = load_context(CONTEXT.SUBSITES[subsite_name], CONTEXT)
        else:
            subsite_context = CONTEXT
        plugins.load_plugins(subsite_context)
        subsite_context.BASE_FOLDER    = os.path.join(CONTEXT.SOURCE_FOLDER, subsite)
        subsite_context.SOURCE_FOLDER  = os.path.join(CONTEXT.SOURCE_FOLDER, subsite)
        subsite_context.OUTPUT_FOLDER  = os.path.join(CONTEXT.OUTPUT_FOLDER, subsite_name)
        subsite_context.CACHE_LOCATION = os.path.join(CONTEXT.BASE_FOLDER, 'cache_' + subsite_name + '.pickle')
        site = Site(subsite_context)
        site.build_site()

    logger.success("Completed everything in %.3f seconds", (time.time() - time_all))

if __name__== "__main__":
  main()