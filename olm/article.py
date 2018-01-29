import os
import datetime
import codecs
import re

INDENTATION = re.compile(r'\n\s{2,}')
META = re.compile(r'^(\w+):\s*(.+?)\n')

def md_parse_meta(text):
    """Parse the given text into metadata and strip it for a Markdown parser.
    :param text: text to be parsed
    """
    rv = {}
    m = META.match(text)

    while m:
        key = m.group(1)
        value = m.group(2)
        value = INDENTATION.sub('\n', value.strip())
        rv[key] = value
        text = text[len(m.group(0)):]
        m = META.match(text)

    return rv, text

class Article:
    """Object representing an article"""

    def __init__(self, context, filepath):
        self.source_filepath = filepath
        dirname = os.path.dirname(filepath)
        basename, extension = os.path.splitext(filepath)
        self.template = context["JINJA_ENV"].get_template('article.html')
        rel_path = os.path.relpath(os.path.join(dirname, basename) + '.html', context["SOURCE_FOLDER"])
        self.output_filepath = os.path.join(context["OUTPUT_FOLDER"], rel_path)
        with codecs.open(filepath, 'r', encoding='utf8') as md_file:
            self.metadata, raw_content = md_parse_meta(md_file.read())
            self.content = context["MD"](raw_content)

    def write_file(self):
        """Write the article to a file"""
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        with codecs.open(self.output_filepath, 'w', encoding='utf-8') as html_file:
            html = self.template.render(article={"content": self.content, "date": datetime.datetime.now(), "metadata": self.metadata})
            html_file.write(html)
