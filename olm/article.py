import os
import datetime
import codecs
import re
from urllib.parse import urljoin

from olm.constants import ArticleStatus
from olm.signals import Signal, signals
from olm.reader import Reader
from olm.writer import Writer
from olm.helper import merge_dictionaries

class Article:
    """Object representing an article"""
    def __repr__(self):
        return self.output_filepath

    def __init__(self, context, filepath=None, metadata=None, content=None, basename=None):
        if filepath is not None:
            self.filepath = filepath
            # Get filenames, paths etc
            self.dirname = os.path.dirname(filepath)
            self.basepath, self.filename = os.path.split(filepath)
            self.basename, self.extension = os.path.splitext(self.filename)
            self.relpath = os.path.relpath(os.path.join(self.dirname, self.basename) + '.html', context.SOURCE_FOLDER)
            
            # Parse the file for content and metadata
            with codecs.open(filepath, 'r', encoding='utf8') as md_file:
                reader = Reader(md_file.read())
                metadata, raw_content = reader.parse()

        elif metadata is not None and content is not None and basename is not None:
            raw_content = content
            self.basename = basename
        else:
            raise Exception('Article object not supplied with either filepath or content and metadata.') 
        
        #TODO: this doesnt seem to work
        signal_sender = Signal(signals.BEFORE_MD_CONVERT)
        signal_sender.send(context=context, content=raw_content)
        
        self.content = context.MD(raw_content)
        self.metadata = metadata

        # Set article variables from metadata
        self.date       = datetime.datetime.strptime(self.metadata['date'].strip(), '%Y-%m-%d') if 'date' in self.metadata else datetime.datetime.now()
        self.type       = self.metadata['type'].strip().lower() if 'type' in self.metadata else None
        self.title      = self.metadata['title'] if 'title' in self.metadata else basename
        self.summary    = context.MD(self.metadata['summary']) if 'summary' in self.metadata else None
        self.location   = self.metadata['location'].strip().lower() if 'location' in self.metadata else None
        status          = self.metadata['status'].strip().lower() if 'status' in self.metadata else None
        if status == 'unlisted' or self.type == 'unlisted':
            self.status = ArticleStatus.UNLISTED
        elif status == 'draft':
            self.status = ArticleStatus.DRAFT
        else:
            self.status = ArticleStatus.ACTIVE
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
        # Work out other variables
        self.template        = 'article.html'
        self.source_filepath = filepath
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
        self.context = context

        self.cache_id = self.output_filepath
        self.same_as_cache = False

        signal_sender = Signal(signals.AFTER_ARTICLE_READ)
        signal_sender.send(context=context, article=self)

    def write_file(self, context=None):
        if self.same_as_cache:
            #logger.debug('%s %s is same as cache. Not writing.', self.title, self.date)
            return
        self.context = context if context is not None else self.context
        """Write the article to a file"""
        signal_sender = Signal(signals.BEFORE_ARTICLE_WRITE)
        signal_sender.send(context=self.context, article=self)
        writer = Writer(
            self.context, 
            self.output_filepath, 
            self.template,
            article=self)
        writer.write_file()