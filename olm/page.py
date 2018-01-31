import os
from os.path import dirname, splitext, relpath, join
import datetime
import codecs
import re
from helper import md_parse_meta

class Page:
    """Object representing an article"""

    def __init__(self, context, filepath=None):
        dirname = os.path.dirname(filepath)
        basepath, filename = os.path.split(filepath)
        basename, extension = os.path.splitext(filename)
        relpath = os.path.relpath(os.path.join(dirname, basename) + '.html', context["SOURCE_FOLDER"])
        
        with codecs.open(filepath, 'r', encoding='utf8') as md_file:
            self.metadata, raw_content = md_parse_meta(md_file.read())
            self.content = context["MD"](raw_content)
        self.source_filepath = filepath
        self.template        = context["JINJA_ENV"].get_template('article.html')
        self.title           = self.metadata['Title'] if 'Title' in self.metadata else base_name
        self.url             = relpath
        self.output_filepath = join(context["OUTPUT_FOLDER"], relpath)


    def write_file(self):
        """Write the article to a file"""
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        with codecs.open(self.output_filepath, 'w', encoding='utf-8') as html_file:
            html = self.template.render(article={"content": self.content, "date": datetime.datetime.now(), "metadata": self.metadata})
            html_file.write(html)
