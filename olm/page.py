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
        self.title           = self.metadata['title'] if 'title' in self.metadata else basename
        self.url             = self.relpath
        self.output_filepath = join(context.OUTPUT_FOLDER, self.relpath)

        self.cache_id = self.output_filepath
        self.cache_type = 'PAGE'

        signal_sender = Signal(signals.AFTER_PAGE_READ)
        signal_sender.send(context=context, page=self)


    def write_file(self, context=None):
        changes                = self.context['cache_change_types']
        changed_meta           = self.context['cache_changed_meta']
        refresh_triggers       = self.context['PAGE_REFRESH']
        refresh_meta_triggers  = self.context['PAGE_REFRESH_META']
        if any(i in changes for i in refresh_triggers):
            self.same_as_cache = False
        if any(any(m in merge_dictionaries(*c) for m in refresh_meta_triggers) for c in changed_meta):
            self.same_as_cache = False
        super().write_file(context, page=self)
        return not self.same_as_cache