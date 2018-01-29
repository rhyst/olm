import sys
import os
import logging
import mistune
from jinja2 import Environment, FileSystemLoader, select_autoescape
import datetime
from article import Article
import time

if len(sys.argv) < 2:
    print("Please identify the source folder")

BASE_FOLDER = os.path.abspath(sys.argv[1])
SOURCE_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'src'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'dist'))
MD = mistune.Markdown()
JINJA_ENV = Environment(
    loader=FileSystemLoader([os.path.join(BASE_FOLDER,'theme/templates')])
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
    i = 1
    logging.info("Scanning source files")
    time_source_scan_start = time.perf_counter()
    for dirname, dirs, files in os.walk(SOURCE_FOLDER):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            basename, extension = os.path.splitext(filename)
            if extension.lower() == ".md":
                print(i)
                i+=1
                logging.debug("Found %s", filepath)
                articles.append(Article(CONTEXT, filepath))
    logging.info("Processed %d articles in %d seconds", len(articles), (time.perf_counter() - time_source_scan_start))

    logging.info("Writing %d files", len(articles))
    time_write_start = time.perf_counter()
    for index, article in enumerate(articles):
        logging.debug("Writing file %d of %d", index + 1, len(articles))
        article.write_file()
    logging.info("Wrote %d articles in %d seconds", len(articles), (time.perf_counter() - time_write_start))

  
if __name__== "__main__":
  main()