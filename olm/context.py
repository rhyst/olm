import os
import sys
import imp
import mistune
import re
from collections import OrderedDict
from olm.helper import Map, merge_ordered_dictionaries
from olm.logger import get_logger
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = get_logger('olm.context')

def load_default_context(path):
    logger.info('Loading default context')
    BASE_FOLDER          = os.path.abspath(path)
    CACHE_LOCATION       = os.path.abspath(os.path.join(BASE_FOLDER)) + os.sep + 'cache.pickle'
    SOURCE_FOLDER        = os.path.abspath(os.path.join(BASE_FOLDER, 'src'))
    STATIC_FOLDER        = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static'))
    CSS_FOLDER           = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static', 'css'))
    JS_FOLDER            = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'static', 'js'))
    TEMPLATES_FOLDER     = os.path.abspath(os.path.join(BASE_FOLDER, 'theme', 'templates'))
    PLUGINS_FOLDER       = os.path.abspath(os.path.join(BASE_FOLDER, 'plugins',))
    MD                   = mistune.Markdown(escape=False)
    JINJA_ENV            = Environment(
                            loader=FileSystemLoader([TEMPLATES_FOLDER])
                            )
    ARTICLE_TYPES        = ['article']
    INDEX_TYPES          = ['index']
    PLUGINS              = []
    SITEURL              = ""
    OUTPUT_FOLDER        = os.path.abspath(os.path.join(BASE_FOLDER, 'dist'))
    OUTPUT_CSS_FOLDER    = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'theme', 'css'))
    OUTPUT_JS_FOLDER     = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'theme', 'js'))
    NO_SCAN              = []
    ARTICLE_WRITE_TRIGGERS      = []
    ARTICLE_META_WRITE_TRIGGERS = []
    PAGE_WRITE_TRIGGERS         = []
    PAGE_META_WRITE_TRIGGERS    = []
    INDEX_WRITE_TRIGGERS        = ["ARTICLE.NEW_FILE"]
    INDEX_META_WRITE_TRIGGERS   = []

    CONTEXT = OrderedDict({
        "BASE_FOLDER":          BASE_FOLDER,
        "CACHE_LOCATION":       CACHE_LOCATION,
        "SOURCE_FOLDER":        SOURCE_FOLDER,
        "OUTPUT_FOLDER":        OUTPUT_FOLDER,
        "STATIC_FOLDER":        STATIC_FOLDER,
        "CSS_FOLDER":           CSS_FOLDER,
        "JS_FOLDER":            JS_FOLDER,
        "MD":                   MD,
        "JINJA_ENV":            JINJA_ENV,
        "ARTICLE_TYPES":        ARTICLE_TYPES,
        "INDEX_TYPES":          INDEX_TYPES,
        "PLUGINS":              PLUGINS,
        "PLUGINS_FOLDER":       PLUGINS_FOLDER,
        "SITEURL":              SITEURL,
        "SUBSITES":             {},
        "OUTPUT_CSS_FOLDER":    OUTPUT_CSS_FOLDER,
        "OUTPUT_JS_FOLDER":     OUTPUT_JS_FOLDER,
        "NO_SCAN":              NO_SCAN,
        "ARTICLE_WRITE_TRIGGERS":      ARTICLE_WRITE_TRIGGERS,
        "ARTICLE_META_WRITE_TRIGGERS": ARTICLE_META_WRITE_TRIGGERS,
        "PAGE_WRITE_TRIGGERS":         PAGE_WRITE_TRIGGERS,
        "PAGE_META_WRITE_TRIGGERS":    PAGE_META_WRITE_TRIGGERS,
        "INDEX_WRITE_TRIGGERS":        INDEX_WRITE_TRIGGERS,
        "INDEX_META_WRITE_TRIGGERS":   INDEX_META_WRITE_TRIGGERS,
    })

    return CONTEXT

def load_context_from_file(settings_file_path, prev_context=None):
    sys_path = sys.path
    sys.path.append(os.path.dirname(settings_file_path))
    py_mod = imp.load_source('settings', settings_file_path)
    user_settings = getattr(py_mod, 'SETTINGS')
    sys.path = sys_path

    return load_context(user_settings, prev_context)


def load_context(context, prev_context=None):
    logger.info('Loading site context')
    
    # Combine default and site settings
    if prev_context is not None:
        CONTEXT = merge_ordered_dictionaries(prev_context, context)
    else:
        CONTEXT = context

    replace_happened = True
    while replace_happened:
        replace_happened = False
        for key in CONTEXT:
            # Do variable substitutions in settings strings
            if isinstance(CONTEXT[key], str):
                value = CONTEXT[key]
                pattern = re.compile(r'{{\s*(\S*)\s*}}')
                for match in re.finditer(pattern, CONTEXT[key]):
                    try:
                        value = value.replace(match.group(0), CONTEXT[match.group(1)])
                        replace_happened = True
                    except KeyError as e:
                        logger.warn("Can't replace '%s' in settings file for key %s", match.group(1), key)
                        logger.warn(e)
                CONTEXT[key] = value

            # Reset the Jinja Env if we have a new templates folder
            if key == "TEMPLATES_FOLDER":
                CONTEXT["JINJA_ENV"] = Environment(
                    loader=FileSystemLoader([CONTEXT[key]])
                )
        
    return Map(CONTEXT)
