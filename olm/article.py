import os
import datetime
import codecs
import re
from helper import md_parse_meta
from urllib.parse import urljoin

class Article:
    """Object representing an article"""

    def __init__(self, context, filepath=None):
        dirname = os.path.dirname(filepath)
        basename, extension = os.path.splitext(filepath)
        rel_path = os.path.relpath(os.path.join(dirname, basename) + '.html', context["SOURCE_FOLDER"])
        
        with codecs.open(filepath, 'r', encoding='utf8') as md_file:
            self.metadata, raw_content = md_parse_meta(md_file.read())
            self.content = context["MD"](raw_content)
        self.date            = datetime.datetime.strptime(self.metadata['Date'].strip(), '%Y-%m-%d') if 'Date' in self.metadata else datetime.datetime.now()
        self.source_filepath = filepath
        self.template        = context["JINJA_ENV"].get_template('article.html')
        self.type            = self.metadata['Type'] if 'Type' in self.metadata else ''
        self.title           = self.metadata['Title'] if 'Title' in self.metadata else basename
        self.summary         = context["MD"](self.metadata['Summary']) if 'Summary' in self.metadata else ''
        self.location        = self.metadata['Location'] if 'Location' in self.metadata else None

        if self.date and self.location:
            output_filename = '{}-{}.html'.format(self.date.strftime('%Y-%m-%d'), self.location.lower())
        else:
            output_filename = '{}.html'.format(basename)
        self.output_filepath = os.path.join(context["OUTPUT_FOLDER"], 'articles', output_filename)
        self.url             = '/articles/{}'.format(output_filename)

    def write_file(self):
        """Write the article to a file"""
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        with codecs.open(self.output_filepath, 'w', encoding='utf-8') as html_file:
            html = self.template.render(article={"content": self.content, "date": datetime.datetime.now(), "metadata": self.metadata})
            html_file.write(html)
