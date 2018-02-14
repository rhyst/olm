import sys
import os
import time
import codecs
import sass
from jsmin import jsmin
from shutil import copyfile

from olm.context import load_context, load_default_context
from olm.plugins import Plugins
from olm.article import Article
from olm.index import Index
from olm.page import Page
from olm.constants import ArticleStatus
from olm.helper import Map
from olm.writer import Writer
from olm.signals import Signal, signals
from olm.logger import get_logger
from olm.cache import check_cache

logger = get_logger('olm.site')

class Site:
    def __init__(self, context):
        self.context = context
        self.subsites = []
    
    def build_site(self):
        # Source markdown files
        CONTEXT = self.context
        all_files = []
        articles = []
        draft_articles = []
        unlisted_articles = []
        pages = []
        subsites = set()

        CONTEXT['authors'] = {}
        CONTEXT['all_files'] = []
        CONTEXT['articles'] = []
        CONTEXT['pages'] = []

        signal_sender = Signal(signals.SITE_INITIALISED)
        signal_sender.send(context=CONTEXT)

        logger.info("Scanning source files")
        time_source_start = time.time()
        for dirname, dirs, files in os.walk(CONTEXT.SOURCE_FOLDER):
            for filename in files:
                filepath = os.path.join(dirname, filename)
                relpath = os.path.relpath(filepath, CONTEXT.SOURCE_FOLDER)
                firstfolder = relpath.split(os.sep)[0]
                basename, extension = os.path.splitext(filename)
                if firstfolder in CONTEXT.NO_SCAN:
                    continue
                if extension.lower() == ".md":
                    if firstfolder[0] == "_":
                        subsites.add(firstfolder)
                    elif firstfolder == "pages":
                        logger.debug("Found %s", filepath)
                        page = Page(CONTEXT, filepath)
                        pages.append(page)
                        all_files.append(page)
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
                        all_files.append(article)
        logger.info("Processed %d articles, %d unlisted articles, %d drafts, and %d pages in %.3f seconds", len(articles), len(unlisted_articles), len(draft_articles), len(pages), time.time() - time_source_start)            

        outputs = []
        for a in articles:
            if a.output_filepath not in outputs:
                outputs.append(a.output_filepath)
            else: 
                dupes = [ b for b in articles if b.output_filepath == a.output_filepath ]
                logger.error("'%s' has the same output file path as '%s'. The other article will be overwritten.", a.source_filepath, dupes[0].source_filepath)

        CONTEXT['all_files'].extend(all_files)
        CONTEXT['articles'].extend(sorted(articles, key=lambda k: (k.date), reverse=True))
        CONTEXT['pages'].extend(pages)

        signal_sender = Signal(signals.BEFORE_CACHING)
        signal_sender.send(context=CONTEXT, articles=CONTEXT.articles)

        check_cache(CONTEXT, CONTEXT['all_files'])
        
        signal_sender = Signal(signals.AFTER_ALL_ARTICLES_READ)
        signal_sender.send(context=CONTEXT, articles=CONTEXT.articles)

        signal_sender = Signal(signals.BEFORE_WRITING)
        signal_sender.send(context=CONTEXT, Writer=Writer)

        logger.info("Writing %d articles", len(CONTEXT.articles))
        time_write_start = time.time()
        for index, article in enumerate(CONTEXT.articles):
            logger.debug("Writing file %d of %d", index + 1, len(CONTEXT.articles))
            article.write_file(context=CONTEXT)
        logger.info("Wrote %d articles in %.3f seconds", len(CONTEXT.articles), (time.time() - time_write_start))

        logger.info("Writing %d pages", len(pages))
        time_write_start = time.time()
        for index, page in enumerate(pages):
            logger.debug("Writing file %d of %d", index + 1, len(pages))
            page.write_file(context=CONTEXT)
        logger.info("Wrote %d pages in %.3f seconds", len(pages), (time.time() - time_write_start))

        # Index
        logger.info("Writing articles index")
        time_write_start = time.time()
        index = Index(CONTEXT)
        index.write_file()
        logger.info("Wrote index in %.3f seconds", (time.time() - time_write_start))

        signal_sender = Signal(signals.AFTER_WRITING)
        signal_sender.send(context=CONTEXT, Writer=Writer)

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
        logger.info("Processed static files in %.3f seconds", time.time() - time_static_start)

        self.subsites = subsites