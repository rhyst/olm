import os
from os.path import dirname, splitext, relpath, join
import datetime
import codecs
import re

from olm.signals import signals, Signal
from olm.source import Source
from olm.helper import merge_dictionaries

class Page(Source):
    """Object representing an article"""

    def __init__(self, context, filepath=None):
        super().__init__(context, filepath)

        self.template        = 'page.html'
        self.title           = self.metadata['title'] if 'title' in self.metadata else self.basename
        self.url             = self.relpath

        if 'PAGE_SLUG' in context:
            slug_dict = vars(self)
            output_filename = context.PAGE_SLUG.format(**slug_dict)
        else:
            output_filename = '{}.html'.format(self.basename)
        
        self.output_filepath = os.path.join(context.OUTPUT_FOLDER, 'pages', output_filename)
        self.url             = 'pages/{}'.format(output_filename)

        self.cache_id = self.output_filepath
        self.cache_type = 'PAGE'
        
        signal_sender = Signal(signals.AFTER_PAGE_READ)
        signal_sender.send(context=context, page=self)

    def calc_cache_status(self, context=None):
        self.context = context if context is not None else self.context
        changes                = self.context['cache_change_types']
        changed_meta           = self.context['cache_changed_meta']
        refresh_triggers       = self.context['PAGE_WRITE_TRIGGERS']
        refresh_meta_triggers  = self.context['PAGE_META_WRITE_TRIGGERS']
        if any(i in changes for i in refresh_triggers):
            self.same_as_cache = False
        if any(any(m in merge_dictionaries(*c) for m in refresh_meta_triggers) for c in changed_meta):
            self.same_as_cache = False

    def write_file(self, context=None):
        self.context = context if context is not None else self.context
        self.calc_cache_status()
        super().write_file(context, page=self)
        return not self.same_as_cache