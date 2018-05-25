import os
import codecs

def quickstart(base_path):
    articles_path  = os.path.join(base_path, 'src', 'articles')
    pages_path     = os.path.join(base_path, 'src', 'pages')
    js_path        = os.path.join(base_path, 'theme', 'static','js')
    css_path       = os.path.join(base_path, 'theme', 'static','css')
    templates_path = os.path.join(base_path, 'theme', 'templates')
    plugins_path   = os.path.join(base_path, 'plugins')
    os.makedirs(articles_path)
    os.makedirs(pages_path)
    os.makedirs(js_path)
    os.makedirs(css_path)
    os.makedirs(templates_path)
    os.makedirs(plugins_path)

    with codecs.open(os.path.join(base_path, 'settings.py'), 'w+', 'utf-8') as f:
        f.write(
'''SETTINGS = {
    "SITEURL": "",
    "SITENAME": "My First Site",
    "SOURCE_FOLDER": "{{BASE_FOLDER}}/src",
    "STATIC_FOLDER": "{{BASE_FOLDER}}/theme/static",
    "TEMPLATES_FOLDER": "{{BASE_FOLDER}}/theme/templates",
    "CSS_FOLDER": "{{BASE_FOLDER}}/theme/static/css",
    "JS_FOLDER": "{{BASE_FOLDER}}/theme/static/js",
    "PLUGINS_FOLDER": "{{BASE_FOLDER}}/plugins",
    "ARTICLE_SLUG": "{date}-{title}.html",
    "PLUGINS": ['pygments_plugin']
}''')
    with codecs.open(os.path.join(articles_path, 'first_article.md'), 'w+', 'utf-8') as f:
        f.write(
'''Title: My First Article
Date: 2018-01-01

This is my first article

Here's some code:

```python
import sys

print(sys.path)
```
''')
    with codecs.open(os.path.join(pages_path, 'about.md'), 'w+', 'utf-8') as f:
        f.write(
'''Title: About
Date: 2018-01-01

This is my website''')
    with codecs.open(os.path.join(templates_path, 'base.html'), 'w+', 'utf-8') as f:
        f.write(
'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="/theme/css/main.css">
<title>{% block title %}{% endblock %}</title>
</head>
<body>
<nav><a href="{{ SITEURL }}/">Home</a> <a href="/pages/about.html">About</a></nav>
<main>
{% block content %}{% endblock %}
</main>
</body>
</html>
''')
    with codecs.open(os.path.join(templates_path, 'article.html'), 'w+', 'utf-8') as f:
        f.write(
'''{% extends "base.html" %}
{% block title %}{{ SITENAME }} - {{ article.title }}{% endblock %}
{% block content %}
<h1>{{article.title}}</h1>
<h2>{{article.date.strftime('%d-%m-%Y')}}</h2>
{{article.content}}
{% endblock %}
''')
    with codecs.open(os.path.join(templates_path, 'page.html'), 'w+', 'utf-8') as f:
        f.write(
'''{% extends "base.html" %}
{% block title %}{{ SITENAME }} - {{ page.title }}{% endblock %}
{% block content %}
<h1>{{page.title}}</h1>
{{page.content}}
{% endblock %}
''')
    with codecs.open(os.path.join(templates_path, 'index.html'), 'w+', 'utf-8') as f:
        f.write(
'''{% extends "base.html" %}
{% block title %}{{ SITENAME }}{% endblock %}

{% block content %}
    <h1>{{ SITENAME }}</h1>
    {% for article in current_page %}
        <div>
            <a href="{{ SITEURL }}/{{ article.url }}">{{ article.title }}</a> - {{  article.date.strftime('%d-%m-%Y') }}
        </div>
    {% endfor %}

  <p class="paginator">
    {% if previous_page is not none %}
    <a href={{ SITEURL }}/{{ previous_page }}>«</a>
    {% endif %}
    Page {{ current_page_number }} / {{ index_pages|length }}
    {% if next_page is not none %}
    <a href={{ SITEURL }}/{{ next_page }}>»</a>
    {% endif %}
  </p> 
{% endblock content %}
''')
    with codecs.open(os.path.join(css_path, 'main.scss'), 'w+', 'utf-8') as f:
        f.write('''
body{
    margin:40px auto;
    max-width:650px;
    line-height:1.6;
    font-size:18px;
    color:#444;
    padding:0 10px
}
h1,h2,h3{
    line-height:1.2
}
''')
    os.makedirs(os.path.join(plugins_path, 'pygments_plugin'))
    with codecs.open(os.path.join(plugins_path, 'pygments_plugin', 'pygments_plugin.py'), 'w+', 'utf-8') as f:
        f.write('''
import re
from olm.signals import signals

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def replace(match):
    language = match.group(2)
    lexer = get_lexer_by_name(language, stripall=True)
    formatter = HtmlFormatter(linenos=True, noclasses=True)
    return highlight(match.group(3), lexer, formatter)

def add_pygments(self, context, source):
    pattern = re.compile(r'(```)(.*)\\n([\w\W]*)(```)', re.MULTILINE)
    source.content = pattern.sub(replace, source.content)

def register():
    return [
        (signals.BEFORE_MD_CONVERT, add_pygments)
    ]
''')