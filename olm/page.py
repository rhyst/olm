import os
from os.path import dirname, splitext, relpath, join
import datetime
import codecs
import re
from olm.signals import signals, Signal
from olm.reader import Reader
from olm.writer import Writer

class Page:
    """Object representing an article"""

    def __init__(self, context, filepath=None):
        dirname = os.path.dirname(filepath)
        basepath, filename = os.path.split(filepath)
        basename, extension = os.path.splitext(filename)
        self.relpath = os.path.relpath(os.path.join(dirname, basename.lower()) + '.html', context.SOURCE_FOLDER)
        
        # Parse the file for content and metadata
        with codecs.open(filepath, 'r', encoding='utf8') as md_file:
            reader = Reader(md_file.read())
            metadata, raw_content = reader.parse()

        self.content = context.MD(raw_content)
        self.metadata = metadata

        self.source_filepath = filepath
        self.template        = 'page.html'
        self.title           = self.metadata['title'] if 'title' in self.metadata else basename
        self.url             = self.relpath
        self.output_filepath = join(context.OUTPUT_FOLDER, self.relpath)
        self.context = context

        self.cache_id = self.output_filepath
        self.same_as_cache = False

        signal_sender = Signal(signals.AFTER_PAGE_READ)
        signal_sender.send(context=context, page=self)


    def write_file(self, context=None):
        if self.same_as_cache:
            #logger.debug('%s %s is same as cache. Not writing.', self.title, self.date)
            return
        
        self.context = context if context is not None else self.context
        writer = Writer(
            self.context, 
            self.output_filepath, 
            self.template,
            page=self)
        writer.write_file()