import re

INDENTATION = re.compile(r'^(\s{4,}|\t{2,})(\S.*)')
META = re.compile(r'^(\w+):\s*(.*)')

class Reader:
    def __init__(self, text):
        self.text = text
        self.metadata = {}
        self.content = ""

    def parse_meta(self):
        """Parse the given text into metadata and strip it for a Markdown parser.
        :param text: text to be parsed
        """
        text = self.text.split('\n')
        meta = {}
        m = META.match(text[0])

        while m:
            key = m.group(1)
            value = m.group(2)
            meta[key] = value
            text = text[1:]
            if len(text) >= 1:
                i = INDENTATION.match(text[0])
                while i:
                    if not isinstance(meta[key], list):
                        meta[key] = [meta[key]]
                    meta[key].append(i.group(2))
                    text = text[1:]
                    i = INDENTATION.match(text[0])
                m = META.match(text[0])
            else:
                m = False

        for key in meta:
            self.metadata[key.lower()] = meta[key].strip() if isinstance(meta[key], str) else meta[key]
        self.content = '\n'.join(text)

        return self.metadata, self.content 