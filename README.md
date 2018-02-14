# Olm

An olm is a cave dwelling amphibian that I imagine is fairly static. Olm the application is a static site generator with a focus on simplicity, speed, and extensibility.

## Features

* Super fast markdown parsing with Mistune
* Easy plugin system based on Blinker signals
* Clever and extensible caching so building is speedy

## Install

Install via pip:

    pip install olm
    
Or run the provided install script:

    ./install

It will install the requirements in a virtualenv.

## Run

If you installed via pip you can run:

    olm [ -s path/to/settings.py] [-d] path/to/site

The `-s` flag allows you to specifiy a different settings file (default is `settings.py` in your site directory). The `-d` flag disables caching so the site is completely regenerated.

Run the provided build script, providing the base folder of your site:

    ./build ../path/to/site

## Content

Olm will scan the `src` directory for markdown files. Any files found in the `pages` directory (or sub-directories) will be treated as a `page`. Any files found in a directory (or sub-directories) beginning with an underscore will be treated as part of a subsite. Any files anywhere else in the `src` directory will be initally treated as an article.

The output html will be placed in the `dist` directory, with articles going into the `articles` directory, pages into the `pages` directory and subsites into a directory with the name of the subsite.

    .
    ├── src
    │   ├── _my_subsite
    │   ├── articles
    │   ├── my_folder
    │   └── pages
    ├── dist
    │   ├── my_subsite
    │   ├── articles
    │   ├── pages
    │   ├── pages
    │   └── index.html
    ├── theme
    └── plugins

## Settings

Below is a list of the settings you can change for your site. Each setting string value can use Jinja style variable replacements to use any setting variables that were defined before it. 

Setting            | Default Value                       | Description
---                | ---                                 | ---
`BASE_FOLDER`      | `sys.argv[1]`                       | The root of the site folder.
`SOURCE_FOLDER`    | `{{BASE_FOLDER}}\src`               | The source folder for all markdown files.
`STATIC_FOLDER`    | `{{BASE_FOLDER}}\theme\static`      | The folder containing css and js.
`TEMPLATES_FOLDER` | `{{BASE_FOLDER}}\theme\templates`   | The folder containing the Jinja templates.
`CSS_FOLDER`       | `{{BASE_FOLDER\theme\static\css}}`  | The folder containing the css files
`JS_FOLDER`        | `{{BASE_FOLDER\theme\static\js}}`   | The folder containing the js files
`PLUGINS_FOLDER`   | `{{BASE_FOLDER}}\plugins`           | The folder containing the plugins.
`ARTICLE_TYPES`    | `['article']`                       | The `type` metadata of files that will be included as articles.
`INDEX_TYPES`      | `['index']`                         | The `type` metadata of files that will be included on the index.
`PLUGINS`          | `[]`                                | List of plugins.
`SITEURL`          | `''`                                | The base url of the site.
`OUTPUT_FOLDER`    | `{{BASE_FOLDER}}\dist`              | The output folder for compiled html and static files.
`OUTPUT_CSS_FOLDER`| `{{OUTPUT_FOLDER}}\theme\css`       | The output folder for compiled css.
`OUTPUT_JS_FOLDER` | `{{OUTPUT_FOLDER}}\theme\js`        | The output folder for compiled js.
`SUBSITES`         | `{}`                                | See subsite section.
`ARTICLE_SLUG`     | `'{location}-{date}.html'`          | The format of article filenames. The curly brace vars can be any Article attribute.

## Themes

Themes are made of two parts; templates and static files. The templates are standard Jinja2 templates. These support all the standard importing/inheritance stuff that you'd expect. 

The statics are css/scss files and javascript files. The css can be scss files which will be compiled and minified. The js will just be minified.

    .
    ├── src
    ├── dist
    ├── theme
    │   ├── static
    │   │   ├── css
    │   │   │   ├── main.scss
    │   │   │   └── _includes.scss
    │   │   └── js
    │   │       ├── navbar.js
    │   │       └── animate.js
    │   └── templates
    │       ├── includes
    │       │   └── sidebar.html
    │       ├── article.html
    │       ├── base.html
    │       ├── index.html
    │       ├── page.html
    └── plugins

## Plugins

Plugins can subscribe to signals to modify data during the build process. The plugin should be in the plugins folder with a directory and python file with the same name: 

    .
    ├── src
    ├── dist
    ├── theme
    └── plugins
        └── mycoolplugin
            └── mycoolplugin.py

## Subsites

### Structure

The content of a subsite should be placed in your `src` directory, in a subdirectory with a name beginning with a an underscore (e.g. `_mysubsite`). Multiple subsites can 
be added. The structure is otherwise the same as a normal site. Within the subsite subdirectory, pages will be drawn from the `pages` subdirectory and all other markdown 
files will be treated initially as articles.

### Settings

Subsites take the same settings that a normal site does. These should be nested under `'SUBSITES'` and your subsite name in your settings.py. e.g.

    SETTINGS = {
        "ARTICLE_SLUG": "{title}.html"
        ...
        "SUBSITES": {
            "mysubsite": {
                "ARTICLE_SLUG": "{date}-{title}.html"
            }
        }
    }

The subsite settings inherit the settings of the main site so you only need overwrite settings you want to be different from the main site.

### Themes

By default the subsite uses the same theme as the main site however you can point it at a different set of templates, css, and js by modifiying the appropriate folder 
settings in the subsite settings e.g.

    'TEMPLATES_FOLDER': os.path.join('{{ BASE_FOLDER }}', 'theme', 'templates', 'subsites', 'mysubsite'),
    'CSS_FOLDER': os.path.join('{{ BASE_FOLDER }}', 'theme', 'static', 'subsites', 'mysubsite', 'css'),
    'JS_FOLDER': os.path.join('{{ BASE_FOLDER }}', 'theme', 'static', 'subsites', 'mysubsite', 'js'),         
    'OUTPUT_CSS_FOLDER': os.path.join('{{ OUTPUT_FOLDER }}', 'theme', 'subsites', 'mysubsite', 'css'),
    'OUTPUT_JS_FOLDER': os.path.join('{{ OUTPUT_FOLDER }}', 'theme', 'subsites', 'mysubsite', 'js'),

### Plugins

By default the subsite will use the same set of plugins as the main site. You can set the "PLUGINS" setting in the subsite settings to a different list of plugins. 
Being able to specify a different plugin path is a TODO.

## Writing plugins

Within the plugin file should be the function with your code and a `register` function which should return a list of tuples with the signal you want to subscribe to and the function that should run. All functions will receive two parameters; `sender` at the moment is just a string with the signal value, and `logger` is a logging function that will let you log within your plugin. All parameters are named so the order doesn't matter.

```python
def mycoolfunction(sender, arg, logger):
    # cool code

def register():
    return ("A_SIGNAL", mycoolfunction)
```

Or:

```python
def mycoolfunction(sender, arg, logger):
    # cool code

def mysecondcoolfunction(sender, arg, logger)
    # more cool code

def register():
    return [
        ("A_SIGNAL", mycoolfunction),
        ("ANOTHER_SIGNAL", mysecondcoolfunction)
    ]
```


### Current signals

Signal Name             | String Value             | Description
---                     |---                       |---
INITIALISED             | `INITIALISED`            | After settings and plugins loaded, before scanning files. Passes context as single argument.
AFTER_ARTICLE_READ      | `AFTER_ARTICLE_READ`     | After each article has been read and been parsed by Mistune for content and metadata. Passes context and the article as arguments.
AFTER_PAGE_READ         | `AFTER_PAGE_READ`        | After each page has been read and been parsed by Mistune for content and metadata. Passes context and the page as arguments.
AFTER_ALL_ARTICLES_READ |`AFTER_ALL_ARTICLES_READ` | After all articles have been read and been parsed by Mistune for content and metadata. Passes context and the list of articles as arguments.
BEFORE_WRITING          | `BEFORE_WRITING`         | After all content is scanned and parsed, before anything is written. Passes context and Writer class as arguments.
BEFORE_ARTICLE_WRITE    | `BEFORE_ARTICLE_WRITE`   | Before each article is written. Passes context and article object as arguments.

### Caching for plugins

## Acknowledgement

Heavily inspired by the [Pelican](https://blog.getpelican.com/) static site generator.
