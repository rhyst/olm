import codecs
import os
from olm.helper import merge_dictionaries

class Writer:
    def __init__(self, context, relative_path, template, **kwargs):
        self.context = context
        self.relative_path = relative_path
        self.template = context.JINJA_ENV.get_template(template)
        self.kwargs = kwargs

        self.output_filepath = os.path.join(context.OUTPUT_FOLDER, relative_path)


    def write_file(self):
        """Write the article to a file"""
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        with codecs.open(self.output_filepath, 'w', encoding='utf-8') as html_file:
            html = self.template.render(**merge_dictionaries(self.context, self.kwargs))
            html_file.write(html)