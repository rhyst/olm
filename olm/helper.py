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
