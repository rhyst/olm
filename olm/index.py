import os
import datetime
import codecs
import re
import math

from olm.writer import Writer
from olm.helper import merge_dictionaries

class Index:
    """Represents an index listing"""

    def __init__(self, context):
        self.context = context
        all_files = context.articles
        self.articles = [ article for article in all_files if article.type in (context.ARTICLE_TYPES + context.INDEX_TYPES) ]
        self.template = context.JINJA_ENV.get_template('index.html')
        self.output_filepath = os.path.join(context.OUTPUT_FOLDER, 'index.html')
        self.paginate()

    def paginate(self):
        num_per_page = 10
        num_pages = math.ceil(len(self.articles)/num_per_page)
        pages = []
        articles = self.articles
        for i in range(0, num_pages):
            page_articles = articles[0:num_per_page]
            articles = articles[num_per_page:]
            pages.append(page_articles)
        self.pages = pages

    def paginated_path(self, page_number, basepath):
        if page_number == 1:
            return os.path.join(basepath, 'index.html'), '/'
        return os.path.join(self.context.OUTPUT_FOLDER,'pg', str(page_number) , 'index.html'), os.path.join('pg', str(page_number))

    def write_file(self):
        """Write the article to a file"""
        cached = True
        changes                = self.context['cache_change_types']
        changed_meta           = self.context['cache_changed_meta']
        refresh_triggers       = self.context['INDEX_WRITE_TRIGGERS']
        refresh_meta_triggers  = self.context['INDEX_META_WRITE_TRIGGERS']

        if any(i in changes for i in refresh_triggers):
            cached = False
        if any(any(m in merge_dictionaries(*c) for m in refresh_meta_triggers) for c in changed_meta):
            cached = False
        if not self.context.caching_enabled:
            cached = False
        if cached:
            return False
        
        dirname = os.path.dirname(self.output_filepath)
        for i, page in enumerate(self.pages):
            for article in page:
                if article.summary:
                    article.summary = self.context.MD(article.summary)
            page_number = i + 1
            output_filepath, url = self.paginated_path(page_number, dirname)
            previous_page = None
            next_page = None
            if i > 0: 
                previous_filepath, previous_page = self.paginated_path(page_number - 1, dirname)
            if i < len(self.pages):
                next_filepath, next_page = self.paginated_path(page_number + 1, dirname)
            writer = Writer(
                self.context, 
                output_filepath, 
                self.template,
                index_pages=self.pages, 
                current_page=page,
                current_page_number=page_number,
                previous_page=previous_page,
                next_page=next_page)
            writer.write_file()
        return True