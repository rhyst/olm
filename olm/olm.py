import sys
import os
import time
import codecs
import sass
from jsmin import jsmin
from shutil import copyfile

from settings import load_settings, load_default_settings
from plugins import Plugins
from article import Article
from index import Index
from page import Page
from constants import ArticleStatus
from helper import Map
from writer import Writer
from signal import Signal, signals

import logging, verboselogs, coloredlogs 
logger = verboselogs.VerboseLogger('olm')
coloredlogs.install(level='INFO', logger=logger, fmt='%(asctime)s [%(name)s] %(message)s')

if len(sys.argv) < 2:
    print("Please identify the source folder")

def generateSite(CONTEXT):
    # Source markdown files
    articles = []
    draft_articles = []
    unlisted_articles = []
    pages = []
    subsites = set()
    logger.info("Scanning source files")
    time_source_start = time.time()
    for dirname, dirs, files in os.walk(CONTEXT.SOURCE_FOLDER):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            relpath = os.path.relpath(filepath, CONTEXT.SOURCE_FOLDER)
            firstfolder = relpath.split(os.sep)[0]
            basename, extension = os.path.splitext(filename)
            if extension.lower() == ".md":
                if firstfolder[0] == "_":
                    subsites.add(firstfolder)
                elif firstfolder == "pages":
                    logger.debug("Found %s", filepath)
                    pages.append(Page(CONTEXT, filepath))
                else:
                    logger.debug("Found %s", filepath)
                    article = Article(CONTEXT, filepath)
                    if article.type in CONTEXT.ARTICLE_TYPES + CONTEXT.INDEX_TYPES:
                        if article.status == ArticleStatus.ACTIVE:
                            articles.append(article)
                        elif article.status == ArticleStatus.UNLISTED:
                            unlisted_articles.append(article)
                        else:
                            draft_articles.append(article)
    logger.info("Processed %d articles, %d unlisted articles, %d drafts, and %d pages in %f seconds", len(articles), len(unlisted_articles), len(draft_articles), len(pages), time.time() - time_source_start)

    signal_sender = Signal(signals.AFTER_ALL_ARTICLES_READ)
    signal_sender.send(context=CONTEXT, articles=articles)

    signal_sender = Signal(signals.BEFORE_WRITING)
    signal_sender.send(context=CONTEXT, Writer=Writer)

    logger.info("Writing %d articles", len(articles))
    time_write_start = time.time()
    for index, article in enumerate(articles):
        logger.debug("Writing file %d of %d", index + 1, len(articles))
        article.write_file()
    logger.info("Wrote %d articles in %f seconds", len(articles), (time.time() - time_write_start))

    logger.info("Writing %d pages", len(pages))
    time_write_start = time.time()
    for index, page in enumerate(pages):
        logger.debug("Writing file %d of %d", index + 1, len(pages))
        page.write_file()
    logger.info("Wrote %d pages in %f seconds", len(pages), (time.time() - time_write_start))

    # Index
    logger.info("Writing articles index")
    CONTEXT.ARTICLES = articles
    index = Index(CONTEXT)
    index.write_file()

    # Static files
    logger.info("Compiling static files")
    time_static_start = time.time()
    sass.compile(dirname=(CONTEXT.CSS_FOLDER, CONTEXT.OUTPUT_CSS_FOLDER), output_style='compressed')
    for dirname, dirs, files in os.walk(CONTEXT.CSS_FOLDER):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            basename, extension = os.path.splitext(filename)
            rel_path = os.path.relpath(filepath, CONTEXT.CSS_FOLDER)
            if extension.lower() == ".css":
                os.makedirs(os.path.dirname(os.path.join(CONTEXT.OUTPUT_CSS_FOLDER, rel_path)), exist_ok=True)
                copyfile(filepath, os.path.join(CONTEXT.OUTPUT_CSS_FOLDER, rel_path))
    for dirname, dirs, files in os.walk(CONTEXT.JS_FOLDER):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            basename, extension = os.path.splitext(filename)
            rel_path = os.path.relpath(filepath, CONTEXT.JS_FOLDER)
            if extension.lower() == ".js":
                with codecs.open(filepath, encoding='utf-8', errors='ignore') as js_file:
                    minified = js_file.read()
                output_filepath = os.path.join(CONTEXT.OUTPUT_JS_FOLDER, rel_path)
                os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                with codecs.open(output_filepath, 'w+', encoding='utf-8') as js_min_file:
                    js_min_file.write(minified)
    logger.info("Processed static files in %f seconds", time.time() - time_static_start)
    return subsites

def main():
    time_all = time.time()
    """Main olm function"""
    logger.info("Beginning static site generation")

    CONTEXT = load_default_settings(sys.argv[1])

    settings_file_path = os.path.abspath(os.path.join(sys.argv[1], 'settings.py'))
    if os.path.isfile(settings_file_path):
        CONTEXT = load_settings(CONTEXT, settings_file_path=settings_file_path)

    plugins = Plugins(CONTEXT)

    signal_sender = Signal(signals.INITIALISED)
    signal_sender.send(context=CONTEXT)

    subsites = generateSite(CONTEXT)

    base_folder = CONTEXT.BASE_FOLDER
    source_folder = CONTEXT.SOURCE_FOLDER
    for subsite in subsites:
        plugins.unload_plugins()
        subsite_name = subsite[1:]
        logger.info("Found subsite '%s'", subsite_name)
        if subsite_name in CONTEXT.SUBSITES:
            subsite_context = load_settings(CONTEXT, settings=CONTEXT.SUBSITES[subsite_name])
        else:
            subsite_context = CONTEXT
        plugins.load_plugins(subsite_context)
        subsite_context.OUTPUT_FOLDER = os.path.abspath(os.path.join(base_folder, 'dist', subsite_name))
        subsite_context.BASE_FOLDER = os.path.join(source_folder, subsite)
        subsite_context.SOURCE_FOLDER = os.path.join(source_folder, subsite)
        generateSite(subsite_context)

    logger.success("Completed everything in %f seconds", (time.time() - time_all))

if __name__== "__main__":
  main()