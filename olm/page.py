import os
from os.path import dirname, splitext, relpath, join
import datetime
import codecs
import re
from olm.signals import signals, Signal
from olm.source import Source

class Page(Source):
    """Object representing an article"""

    def __init__(self, context, filepath=None):
        super().__init__(context, filepath)

        self.template        = 'page.html'
        self.title           = self.metadata['title'] if 'title' in self.metadata else basename
        self.url             = self.relpath
        self.output_filepath = join(context.OUTPUT_FOLDER, self.relpath)

        self.cache_id = self.output_filepath

        signal_sender = Signal(signals.AFTER_PAGE_READ)
        signal_sender.send(context=context, page=self)


    def write_file(self, context=None):
        super().write_file(context, page=self)