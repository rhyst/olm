import os
import datetime
import codecs
import re
from urllib.parse import urljoin
from blinker import signal

from helper import md_parse_meta
from constants import ArticleStatus, Signals

class Article:
    """Object representing an article"""
    def __repr__(self):
        return self.output_filepath

    def __init__(self, context, filepath=None):
        # Get filenames, paths etc.
        dirname = os.path.dirname(filepath)
        basepath, filename = os.path.split(filepath)
        basename, extension = os.path.splitext(filename)
        relpath = os.path.relpath(os.path.join(dirname, basename) + '.html', context.SOURCE_FOLDER)
        
        # Parse the file for content and metadata
        with codecs.open(filepath, 'r', encoding='utf8') as md_file:
            raw_metadata, raw_content = md_parse_meta(md_file.read())

        self.content = context.MD(raw_content)
        self.metadata = {}
        for key in raw_metadata.keys():
            self.metadata[key.lower()] = raw_metadata[key].strip()
        
        # Set article variables from metadata
        self.date            = datetime.datetime.strptime(self.metadata['date'].strip(), '%Y-%m-%d') if 'date' in self.metadata else datetime.datetime.now()
        self.type            = self.metadata['type'].strip().lower() if 'type' in self.metadata else ''
        self.title           = self.metadata['title'] if 'title' in self.metadata else basename
        self.summary         = context.MD(self.metadata['summary']) if 'summary' in self.metadata else ''
        self.location        = self.metadata['location'].strip().lower() if 'location' in self.metadata else None
        status          = self.metadata['status'].strip().lower() if 'status' in self.metadata else None
        if status == 'unlisted' or self.type == 'unlisted':
            self.status = ArticleStatus.UNLISTED
        elif status == 'draft':
            self.status = ArticleStatus.DRAFT
        else:
            self.status = ArticleStatus.ACTIVE
        
        # Work out other variables
        self.template        = context.JINJA_ENV.get_template('article.html')
        self.source_filepath = filepath
        if self.date and self.location:
            output_filename = '{}-{}.html'.format(self.location.lower(), self.date.strftime('%Y-%m-%d'))
        else:
            output_filename = '{}.html'.format(basename)

        self.output_filepath = os.path.join(context.OUTPUT_FOLDER, 'articles', output_filename)
        self.url             = 'articles/{}'.format(output_filename)

        signal_sender = signal(Signals.AFTER_ARTICLE_READ)
        signal_sender.send((context, self))

    def write_file(self):
        """Write the article to a file"""
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        with codecs.open(self.output_filepath, 'w', encoding='utf-8') as html_file:
            html = self.template.render(article={"content": self.content, "date": datetime.datetime.now(), "metadata": self.metadata})
            html_file.write(html)
