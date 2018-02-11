import re

INDENTATION = re.compile(r'^(\s{4,}|\t{2,})(\S.*)')
META = re.compile(r'^(\w+):\s*(.*)')

class Reader:
    def __init__(self, text):
        self.text = text
        self.metadata = {}
        self.content = ""
        self.keys = []

    def parse(self):
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
        content = '\n'.join(text)
        #TODO: make TOC optional?
        self.content = self.generate_toc(content)

        return self.metadata, self.content 

    def get_id(self, title):
        link_id = title
        index = 0
        while link_id in self.keys:
            index = index + 1
            link_id = title + '_' + str(index)
        self.keys.append(link_id)
        return link_id

    def generate_toc(self, content):
        pattern = re.compile(r'\[TOC\]')
        # Only run if [TOC] in text
        if pattern.search(content):
            replacements = []     
            lines =  content.split('\n')
            min = None
            headers = []
            hashpattern = re.compile(r'(#+)(.*)')
            # Find all headers and their place in the text, and
            # the minimum header number
            for index, line in enumerate(lines):
                if line.startswith('#'):
                    match = hashpattern.match(line)
                    no_of_hashes = len(match.group(1))
                    title = match.group(2).strip()
                    if min is None or no_of_hashes < min:
                        min = no_of_hashes
                    headers.append((index, no_of_hashes, title))
            output = ''
            prev_depth = 0
            for header in headers:
                index = header[0]
                no_of_hashes = header[1]
                depth = no_of_hashes - min + 1
                title = header[2]
                # Get unique id for header link
                link_id = self.get_id(title)
                # Replace markdown header with html header + id
                html_header = '<h{no_of_hashes} id="{link_id}">{title}</h{no_of_hashes}>\n'.format(title=title, link_id=link_id, no_of_hashes=no_of_hashes)
                replacements.append((index, html_header))
                # Construct list of header links by comparing
                # adjacent header numbers as list depth
                if prev_depth < depth:
                    for i in range(prev_depth, depth):
                        output = output + '<ul>\n'
                    output = output + '<li><a href="#{}">{}</a></li>\n'.format(link_id, title)
                elif prev_depth == depth:
                    output = output + '<li><a href="#{}">{}</a></li>\n'.format(link_id, title)
                elif prev_depth > depth:
                    for i in range(depth, prev_depth):
                        output = output + '</ul>\n'
                    output = output + '<li><a href="#{}">{}</a></li>\n'.format(link_id, title)
                prev_depth = depth  
            for i in range(0, prev_depth):
                output = output + '</ul>\n'
            # First replace all markdown headers so that the line
            # numbers are correct
            for replacement in replacements:
                lines[replacement[0]] = replacement[1]
            # Then replace [TOC] with the generated TOC
            return pattern.sub(output, '\n'.join(lines))
        else:
            return content