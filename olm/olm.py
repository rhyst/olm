import sys
import os
import logging
import mistune
import datetime
import time
import codecs
from jinja2 import Environment, FileSystemLoader, select_autoescape
import sass
from jsmin import jsmin
from blinker import signal
import imp

from article import Article
from index import Index
from page import Page
from constants import ArticleStatus, Signals
from helper import Map
from writer import Writer

if len(sys.argv) < 2:
    print("Please identify the source folder")

BASE_FOLDER = os.path.abspath(sys.argv[1])
SOURCE_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'src'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'dist'))
STATIC_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static'))
TEMPLATES_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'templates'))
PLUGINS_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'plugins',))
MD = mistune.Markdown()
JINJA_ENV = Environment(
    loader=FileSystemLoader([TEMPLATES_FOLDER])
)
ARTICLE_TYPES = ['trip', 'tour']
INDEX_TYPES = ['index', 'stickyindex']
PLUGINS = ['inlinephotos', 'acyear', 'cavepeeps']
BASE_URL = "/"

CONTEXT = Map({
    "BASE_FOLDER": BASE_FOLDER,
    "SOURCE_FOLDER": SOURCE_FOLDER,
    "OUTPUT_FOLDER": OUTPUT_FOLDER,
    "MD": MD,
    "JINJA_ENV": JINJA_ENV,
    "ARTICLE_TYPES": ARTICLE_TYPES,
    "INDEX_TYPES": INDEX_TYPES,
    "PLUGINS": PLUGINS,
    "PLUGINS_FOLDER": PLUGINS_FOLDER,
    "BASE_URL": "/",
    "BADGES": {
        'lightning': {
            'src': 'lightning.png',
            'alt': 'In the bivi'
        }
    },
    "authors": set()
})

def loadPlugins():
    for plugin in CONTEXT['PLUGINS']:
        try:
            path = os.path.join(CONTEXT.PLUGINS_FOLDER, plugin, plugin + '.py')
            py_mod = imp.load_source(plugin, path)
            registrations = getattr(py_mod, 'register')()
            if type(registrations) is tuple:
                registrations = [ registrations ]
            for registration in registrations:
                # TODO: Check if valid signal
                signal_sender = signal(registration[0])
                signal_sender.connect(registration[1])
        except Exception as e:
            logging.warn('Plugin %s failed to load.', plugin)
            logging.warn(e)

def generateSite():
     # Source markdown files
    articles = []
    draft_articles = []
    unlisted_articles = []
    pages = []
    subsites = set()
    logging.info("Scanning source files")
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
                    logging.debug("Found %s", filepath)
                    pages.append(Page(CONTEXT, filepath))
                else:
                    logging.debug("Found %s", filepath)
                    article = Article(CONTEXT, filepath)
                    if article.type in CONTEXT.ARTICLE_TYPES:
                        if article.status == ArticleStatus.ACTIVE:
                            articles.append(article)
                        elif article.status == ArticleStatus.UNLISTED:
                            unlisted_articles.append(article)
                        else:
                            draft_articles.append(article)
    logging.info("Processed %d articles, %d unlisted articles, %d drafts, and %d pages in %f seconds", len(articles), len(unlisted_articles), len(draft_articles), len(pages), time.time() - time_source_start)
    
    signal_sender = signal(Signals.AFTER_ALL_ARTICLES_READ)
    signal_sender.send((CONTEXT, articles))

    signal_sender = signal(Signals.BEFORE_WRITING)
    signal_sender.send((CONTEXT, Writer))

    logging.info("Writing %d articles", len(articles))
    time_write_start = time.time()
    for index, article in enumerate(articles):
        logging.debug("Writing file %d of %d", index + 1, len(articles))
        article.write_file()
    logging.info("Wrote %d articles in %f seconds", len(articles), (time.time() - time_write_start))

    logging.info("Writing %d pages", len(pages))
    time_write_start = time.time()
    for index, page in enumerate(pages):
        logging.debug("Writing file %d of %d", index + 1, len(pages))
        page.write_file()
    logging.info("Wrote %d pages in %f seconds", len(pages), (time.time() - time_write_start))

    # Index
    logging.info("Writing articles index")
    CONTEXT.ARTICLES = articles
    index = Index(CONTEXT)
    index.write_file()

    # Static files
    logging.info("Compiling static files")
    time_static_start = time.time()
    sass.compile(dirname=(os.path.join(STATIC_FOLDER, 'css'), os.path.join(OUTPUT_FOLDER, 'theme', 'css')), output_style='compressed')
    for dirname, dirs, files in os.walk(os.path.join(STATIC_FOLDER, 'js')):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            basename, extension = os.path.splitext(filename)
            rel_path = os.path.relpath(filepath, os.path.join(STATIC_FOLDER, 'js'))
            if extension.lower() == ".js":
                with codecs.open(filepath, encoding='utf-8', errors='ignore') as js_file:
                    minified = js_file.read() #jsmin(js_file.read())
                output_filepath = os.path.join(OUTPUT_FOLDER, 'theme', 'js', rel_path)
                os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                with codecs.open(output_filepath, 'w+', encoding='utf-8') as js_min_file:
                    js_min_file.write(minified)
    logging.info("Processed static files in %f seconds", time.time() - time_static_start)
    return subsites

def main():
    time_all = time.time()
    """Main olm function"""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.info("Beginning static site generation")

    loadPlugins()

    signal_sender = signal(Signals.INITIALISED)
    signal_sender.send((CONTEXT))

    subsites = generateSite()
    for subsite in subsites:
        logging.info("Found subsite '%s'", subsite[1:])
        CONTEXT.OUTPUT_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'dist', subsite[1:]))
        CONTEXT.BASE_FOLDER = os.path.join(SOURCE_FOLDER, subsite)
        CONTEXT.SOURCE_FOLDER = os.path.join(SOURCE_FOLDER, subsite)
        generateSite()

    logging.info("Completed everything in %f seconds", (time.time() - time_all))

if __name__== "__main__":
  main()