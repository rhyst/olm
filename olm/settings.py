import os
import imp
import mistune
import re
from helper import Map
from jinja2 import Environment, FileSystemLoader, select_autoescape
from logger import get_logger

logger = get_logger('olm.settings')

def load_default_settings(path):
    logger.info('Loading default settings')
    BASE_FOLDER         = os.path.abspath(path)
    SOURCE_FOLDER       = os.path.abspath(os.path.join(BASE_FOLDER, 'src'))
    STATIC_FOLDER       = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static'))
    CSS_FOLDER          = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static', 'css'))
    JS_FOLDER           = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static', 'js'))
    TEMPLATES_FOLDER    = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'templates'))
    PLUGINS_FOLDER      = os.path.abspath(os.path.join(BASE_FOLDER, 'plugins',))
    MD                  = mistune.Markdown()
    JINJA_ENV           = Environment(
                            loader=FileSystemLoader([TEMPLATES_FOLDER])
                            )
    ARTICLE_TYPES       = ['article']
    INDEX_TYPES         = ['index']
    PLUGINS             = []
    SITEURL             = ""
    OUTPUT_FOLDER       = os.path.abspath(os.path.join(BASE_FOLDER, 'dist'))
    OUTPUT_CSS_FOLDER   = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'theme', 'css'))
    OUTPUT_JS_FOLDER    = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'theme', 'js'))

    CONTEXT = Map({
        "BASE_FOLDER": BASE_FOLDER,
        "SOURCE_FOLDER": SOURCE_FOLDER,
        "OUTPUT_FOLDER": OUTPUT_FOLDER,
        "STATIC_FOLDER": STATIC_FOLDER,
        "CSS_FOLDER": CSS_FOLDER,
        "JS_FOLDER": JS_FOLDER,
        "MD": MD,
        "JINJA_ENV": JINJA_ENV,
        "ARTICLE_TYPES": ARTICLE_TYPES,
        "INDEX_TYPES": INDEX_TYPES,
        "PLUGINS": PLUGINS,
        "PLUGINS_FOLDER": PLUGINS_FOLDER,
        "SITEURL": SITEURL,
        "SUBSITES": {},
        "OUTPUT_CSS_FOLDER": OUTPUT_CSS_FOLDER,
        "OUTPUT_JS_FOLDER": OUTPUT_JS_FOLDER,
        "authors": set()
    })

    return CONTEXT

def load_settings(CONTEXT, settings_file_path=None, settings=None):
    logger.info('Loading site settings')

    # Load the file and extract the settings dict
    if (settings_file_path is not None):
        py_mod = imp.load_source('settings', settings_file_path)
        user_settings = getattr(py_mod, 'SETTINGS')
    else:
        user_settings = settings
    
    # Combine default and site settings
    CONTEXT = Map({**CONTEXT, **user_settings})

    for key in CONTEXT:
        # Do variable substitutions in settings strings
        if isinstance(CONTEXT[key], str):
            value = CONTEXT[key]
            pattern = re.compile(r'{{\s*(\S*)\s*}}')
            for match in re.finditer(pattern, CONTEXT[key]):
                try:
                    value = value.replace(match.group(0), CONTEXT[match.group(1)])
                except KeyError as e:
                    logger.warn("Can't replace '%s' in settings file for key %s", match.group(1), key)
                    logger.warn(e)
            CONTEXT[key] = value

        # Reset the Jinja Env if we have a new templates folder
        if key == "TEMPLATES_FOLDER":
            CONTEXT["JINJA_ENV"] = Environment(
                loader=FileSystemLoader([CONTEXT[key]])
            )
    return CONTEXT
