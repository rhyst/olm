import sys
import os
import logging
import mistune
from jinja2 import Environment, FileSystemLoader, select_autoescape
import datetime
from article import Article
import time
import sass
from jsmin import jsmin
import codecs

if len(sys.argv) < 2:
    print("Please identify the source folder")

BASE_FOLDER = os.path.abspath(sys.argv[1])
SOURCE_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'src'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'dist'))
STATIC_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static'))
TEMPLATES_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'templates'))
MD = mistune.Markdown()
JINJA_ENV = Environment(
    loader=FileSystemLoader([TEMPLATES_FOLDER])
)
CONTEXT = {
    "BASE_FOLDER": BASE_FOLDER,
    "SOURCE_FOLDER": SOURCE_FOLDER,
    "OUTPUT_FOLDER": OUTPUT_FOLDER,
    "MD": MD,
    "JINJA_ENV": JINJA_ENV
}

def main():
    """Main olm function"""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.info("Beginning static site generation")

    articles = []
    logging.info("Scanning source files")
    time_source_start = time.time()
    for dirname, dirs, files in os.walk(SOURCE_FOLDER):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            basename, extension = os.path.splitext(filename)
            if extension.lower() == ".md":
                logging.debug("Found %s", filepath)
                articles.append(Article(CONTEXT, filepath))
    logging.info("Processed %d articles in %f seconds", len(articles), time.time() - time_source_start)

    logging.info("Writing %d files", len(articles))
    time_write_start = time.time()
    for index, article in enumerate(articles):
        logging.debug("Writing file %d of %d", index + 1, len(articles))
        article.write_file()
    logging.info("Wrote %d articles in %f seconds", len(articles), (time.time() - time_write_start))

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
                    minified = jsmin(js_file.read())
                output_filepath = os.path.join(OUTPUT_FOLDER, 'theme', 'js', rel_path)
                os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                with codecs.open(output_filepath, 'w+', encoding='utf-8') as js_min_file:
                    js_min_file.write(minified)
    logging.info("Processed static files in %f seconds", time.time() - time_static_start)
  
if __name__== "__main__":
  main()