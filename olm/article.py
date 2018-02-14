import os
import datetime
import codecs
import re
from urllib.parse import urljoin

from olm.constants import ArticleStatus
from olm.signals import Signal, signals
from olm.helper import merge_dictionaries
from olm.source import Source

class Article(Source):
    """ Represents an article"""
    def __repr__(self):
        return self.output_filepath

    def __init__(self, context, filepath=None, metadata=None, content=None, basename=None):
        if filepath is not None:
            super().__init__(context, filepath=filepath)
        elif metadata is not None and content is not None and basename is not None:
            super().__init__(context, metadata=metadata, content=content, basename=basename)

        self.template   = 'article.html'
        self.date       = datetime.datetime.strptime(self.metadata['date'].strip(), '%Y-%m-%d') if 'date' in self.metadata else datetime.datetime.now()
        self.type       = self.metadata['type'].strip().lower() if 'type' in self.metadata else None
        self.title      = self.metadata['title'] if 'title' in self.metadata else basename
        self.summary    = context.MD(self.metadata['summary']) if 'summary' in self.metadata else None
        self.location   = self.metadata['location'].strip().lower() if 'location' in self.metadata else None
        
        # Status
        status          = self.metadata['status'].strip().lower() if 'status' in self.metadata else None
        if status == 'unlisted' or self.type == 'unlisted':
            self.status = ArticleStatus.UNLISTED
        elif status == 'draft':
            self.status = ArticleStatus.DRAFT
        else:
            self.status = ArticleStatus.ACTIVE
        
        # Authors
        if 'authors' in self.metadata:
            self.authors = [a.strip() for a in self.metadata['authors'].split(',')]
        elif 'author' in self.metadata:
            self.authors = [a.strip() for a in self.metadata['author'].split(',')]
        else:
            self.authors = []
        for author in self.authors:
            if author in context['authors']:
                context['authors'][author].append(self)
            else:
                context['authors'][author] = [self]

        # Output Filepath
        if self.date and self.location:
            if 'ARTICLE_SLUG' in context:
                slug_dict = merge_dictionaries(vars(self), {'date': self.date.strftime('%Y-%m-%d'), 'location': self.location.lower()})
                output_filename = context.ARTICLE_SLUG.format(**slug_dict)
            else:
                output_filename = '{}-{}.html'.format(self.location.lower(), self.date.strftime('%Y-%m-%d'))
        else:
            output_filename = '{}.html'.format(self.basename)
        self.output_filepath = os.path.join(context.OUTPUT_FOLDER, 'articles', output_filename)
        self.url             = 'articles/{}'.format(output_filename)

        self.cache_id = self.output_filepath
        self.cache_type = 'ARTICLE'

        signal_sender = Signal(signals.AFTER_ARTICLE_READ)
        signal_sender.send(context=context, article=self)

    def write_file(self, context=None):
        super().write_file(context, article=self)