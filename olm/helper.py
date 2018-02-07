import re

INDENTATION = re.compile(r'^(\s{4,}|\t{2,})(.*)')
META = re.compile(r'^(\w+):\s*(.*)')

def md_parse_meta(text):
    """Parse the given text into metadata and strip it for a Markdown parser.
    :param text: text to be parsed
    """
    text = text.split('\n')
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
                meta[key] = meta[key] + i.group(1)
                text = text[1:]
                i = INDENTATION.match(text[0])
            m = META.match(text[0])
        else:
            m = False

    return meta, '\n'.join(text)

class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]