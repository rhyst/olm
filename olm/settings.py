import os
import imp
import mistune
from jinja2 import Environment, FileSystemLoader, select_autoescape
from helper import Map

def load_default_settings(path):
    BASE_FOLDER = os.path.abspath(path)
    SOURCE_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'src'))
    OUTPUT_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'dist'))
    STATIC_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static'))
    TEMPLATES_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'templates'))
    PLUGINS_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER, 'plugins',))
    MD = mistune.Markdown()
    JINJA_ENV = Environment(
        loader=FileSystemLoader([TEMPLATES_FOLDER])
    )
    ARTICLE_TYPES = ['article']
    INDEX_TYPES = ['index']
    PLUGINS = []
    SITEURL = "/"

    CONTEXT = Map({
        "BASE_FOLDER": BASE_FOLDER,
        "SOURCE_FOLDER": SOURCE_FOLDER,
        "OUTPUT_FOLDER": OUTPUT_FOLDER,
        "STATIC_FOLDER": STATIC_FOLDER,
        "MD": MD,
        "JINJA_ENV": JINJA_ENV,
        "ARTICLE_TYPES": ARTICLE_TYPES,
        "INDEX_TYPES": INDEX_TYPES,
        "PLUGINS": PLUGINS,
        "PLUGINS_FOLDER": PLUGINS_FOLDER,
        "SITEURL": SITEURL,
        "authors": set()
    })

    return CONTEXT

def load_settings(site_path, settings_file_path=None):
    CONTEXT = load_default_settings(site_path)
    if (settings_file_path is None):
        return CONTEXT
    py_mod = imp.load_source('settings', settings_file_path)
    user_settings = getattr(py_mod, 'SETTINGS')
    for key in user_settings:
        CONTEXT[key] = user_settings[key]
    return CONTEXT
    #registrations = getattr(py_mod, 'register')()