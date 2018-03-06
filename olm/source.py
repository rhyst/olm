import os
import codecs
from olm.reader import Reader
from olm.writer import Writer
from olm.signals import Signal, signals

class Source:
    """ Represents any markdown source file in the site e.g. an Article or a Page """
    def __init__(self, context, filepath=None, metadata=None, content=None, basename=None):
        self.context = context
        if filepath is not None:
            self.source_filepath = filepath
            # Get filenames, paths etc
            self.dirname = os.path.dirname(filepath)
            self.basepath, self.filename = os.path.split(filepath)
            self.basename, self.extension = os.path.splitext(self.filename)
            self.relpath = os.path.relpath(os.path.join(self.dirname, self.basename) + '.html', context.SOURCE_FOLDER)
            
            # Parse the file for content and metadata
            with codecs.open(filepath, 'r', encoding='utf8') as md_file:
                reader = Reader(md_file.read())
                metadata, content = reader.parse()

        elif metadata is not None and content is not None and basename is not None:
            self.content = content
            self.basename = basename
            self.source_filepath = None
            self.dirname  = None
            self.basepath = None
            self.relpath  = None

        else:
            raise Exception('Article object not supplied with either filepath or content and metadata.') 
        
        #TODO: this doesnt seem to work
        #signal_sender = Signal(signals.BEFORE_MD_CONVERT)
        #signal_sender.send(context=context, content=raw_content)
        self.content = content
        self.metadata = metadata
        self.status = None
        self.template = None
        self.output_filepath = None
        self.same_as_cache = False
        self.cache_type = 'SOURCE'
    
    def calc_cache_status(self, context=None):
        self.context = context if context is not None else self.context
        return self.same_as_cache

    def write_file(self, context=None, **kwargs):
        self.context = context if context is not None else self.context
        if self.context.caching_enabled and self.same_as_cache:
            return
        if self.template is None:
            return
        self.content = context.MD(self.content)
        writer = Writer(
            self.context, 
            self.output_filepath, 
            self.template,
            **kwargs)
        writer.write_file()