# Olm

An olm is a cave dwelling amphibian that I imagine is fairly static. This is a fast, featureful, static site generator.

## Install

Run the provided install script:

    ./install

It will install the requirements in a virtualenv.

## Run

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

Setting            | Default                             | Description
---                | ---                                 | ---
`BASE_FOLDER`      | `sys.argv[1]`                       | The root of the site folder.
`SOURCE_FOLDER`    | `{{ BASE_FOLDER }}\src`             | The source folder for all markdown files.
`OUTPUT_FOLDER`    | `{{ BASE_FOLDER }}\dist`            | The output folder for compiled html and static files
`STATIC_FOLDER`    | `{{ BASE_FOLDER }}\theme\static`    | The folder containing css and js.
`TEMPLATES_FOLDER` | `{{ BASE_FOLDER }}\theme\templates` | The folder containing the Jinja templates.
`PLUGINS_FOLDER`   | `{{ BASE_FOLDER }}\plugins`         | The folder containing the plugins.
`ARTICLE_TYPES`    | `['article']`                       | The `type` metadata of files that will be included as articles.
`INDEX_TYPES`      | `['index']`                         | The `type` metadata of files that will be included on the index.
`PLUGINS`          | `[]`                                | List of plugins
`SITEURL`          | `''`                                | The base url of the site

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


Within the plugin file should be the function with your code and a `register` function which should return a list of tuples with the signal you want to subscribe to and the function that should run.

```python
def mycoolfunction(arg):
    # cool code

def register():
    return ("A_SIGNAL", mycoolfunction)
```

Or:

```python
def mycoolfunction(arg):
    # cool code

def mysecondcoolfunction(arg)
    # more cool code

def register():
    return [
        ("A_SIGNAL", mycoolfunction),
        ("ANOTHER_SIGNAL", mysecondcoolfunction)
    ]
```

### Current signals

Signal Name | String Value | Description
---|---|---
INITIALISED             | `INITIALISED`            | After settings and plugins loaded, before scanning files. Passes context as single argument.
AFTER_ARTICLE_READ      |`AFTER_ARTICLE_READ`      | After each article has been read and been parsed by Mistune for content and metadata. Passes context and the article as arguments.
AFTER_ALL_ARTICLES_READ |`AFTER_ALL_ARTICLES_READ` | After all articles have been read and been parsed by Mistune for content and metadata. Passes context and the list of articles as arguments.
BEFORE_WRITING          | `BEFORE_WRITING`         | After all content is scanned and parsed, before anything is written. Passes context and Writer class as arguments.
BEFORE_ARTICLE_WRITE    | `BEFORE_ARTICLE_WRITE`   | Before each article is written. Passes context and article object as arguments.

## Acknowledgement

Heavily inspired by the [Pelican](https://blog.getpelican.com/) static site generator.
