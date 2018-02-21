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

    olm path/to/site
Options are:

* `-s` or `--settings`:  Specify a different settings file. Default is `./settings.py`.
* `-d` or `—disable-cache`:  Disables caching so the site is completely regenerated.
* `-l` or `—log-level`: Set the log level. Can be `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, or `CRITICAL`. Default is `INFO`.


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

| Setting                | Default Value                      | Description                              |
| ---------------------- | ---------------------------------- | ---------------------------------------- |
| `BASE_FOLDER`          | `sys.argv[1]`                      | The root of the site folder.             |
| `SOURCE_FOLDER`        | `{{BASE_FOLDER}}\src`              | The source folder for all markdown files. |
| `STATIC_FOLDER`        | `{{BASE_FOLDER}}\theme\static`     | The folder containing css and js.        |
| `TEMPLATES_FOLDER`     | `{{BASE_FOLDER}}\theme\templates`  | The folder containing the Jinja templates. |
| `CSS_FOLDER`           | `{{BASE_FOLDER\theme\static\css}}` | The folder containing the css files      |
| `JS_FOLDER`            | `{{BASE_FOLDER\theme\static\js}}`  | The folder containing the js files       |
| `PLUGINS_FOLDER`       | `{{BASE_FOLDER}}\plugins`          | The folder containing the plugins.       |
| `ARTICLE_TYPES`        | `['article']`                      | The `type` metadata of files that will be included as articles. |
| `INDEX_TYPES`          | `['index']`                        | The `type` metadata of files that will be included on the index. |
| `PLUGINS`              | `[]`                               | List of plugins.                         |
| `SITEURL`              | `''`                               | The base url of the site.                |
| `OUTPUT_FOLDER`        | `{{BASE_FOLDER}}\dist`             | The output folder for compiled html and static files. |
| `OUTPUT_CSS_FOLDER`    | `{{OUTPUT_FOLDER}}\theme\css`      | The output folder for compiled css.      |
| `OUTPUT_JS_FOLDER`     | `{{OUTPUT_FOLDER}}\theme\js`       | The output folder for compiled js.       |
| `SUBSITES`             | `{}`                               | See subsite section.                     |
| `ARTICLE_SLUG`         | `'{location}-{date}.html'`         | The format of article filenames. The curly brace vars can be any Article attribute. |
| `ARTICLE_WRITE_TRIGGERS`      | []                                 | List of cache types that trigger articles to rebuild |
| `ARTICLE_META_WRITE_TRIGGERS` | []                                 | List of metadata keys that trigger articles to rebuild when changed |
| `PAGE_WRITE_TRIGGERS`         | []                                 | List of cache types that trigger pages to rebuild |
| `PAGE_META_WRITE_TRIGGERS`    | []                                 | List of metadata keys that trigger pages to rebuild when changed |
| `INDEX_WRITE_TRIGGERS`        | []                                 | List of cache types that trigger the index to rebuild |
| `INDEX_META_WRITE_TRIGGERS`   | []                                 | List of metadata keys that trigger the index to rebuild when changed |

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

### Caching

Olm will try to avoid rewriting files that do not need to be changed. Writing files is slow, so this helps keep the build times to a minimum. The first time it runs it will generate a cache file. On subsequent runs it will compare files to their cached versions as it reads them. If they are the same then they will not be rewritten. The cache file is update on each run.

However this means that if you have pages that depend on other pages (a index page, or a page that displays some statistics on the articles metadata) then they wouldn't be default be rewritten when an article changes.

When Olm detects that a file has changed it adds it to a list of changes. These changes consist of a 'file type' and a 'change type'. The file type will be something like `ARTICLE` or `PAGE`. The change type will be `CONTENT` or `METADATA`. The change is then something like `ARTICLE.CONTENT` or `PAGE.METADATA`.

Then there is, for example, the `INDEX_WRITE_TRIGGERS` setting. You can set this to a list of changes like [`ARTICLE.METADATA`, `PAGE.METADATA`] and then if any article or page's metadata changes then the index will be rewritten and updated along with the article or page.

If you only want to update when a particular item of metadata changes then that is possible to. Olm also collects a list of the changed metadata and you can set `INDEX_META_WRITE_TRIGGERS` to [`title`, `date`] to only refresh when title or date metadata is updated.

| Change types   | Description |
| `CONTENT`      | Added when the content of any file changes (not including metdata) |
| `METADATA`     | Added when the metadata of any file changes |
| `NEW_FILE`     | Added when there is a new file |
| `REMOVED_FILE` | Added when a file is removed |

| File types | Description |
| `ARTICLE`  | A file of the article type |
| `PAGE`     | A file of the page type    |


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


### Signals

| Signal Name             | String Value              | Description                              |
| ----------------------- | ------------------------- | ---------------------------------------- |
| INITIALISED             | `INITIALISED`             | After settings and plugins loaded, before scanning files. Passes context as single argument. |
| AFTER_ARTICLE_READ      | `AFTER_ARTICLE_READ`      | After each article has been read and been parsed by Mistune for content and metadata. Passes context and the article as arguments. |
| AFTER_PAGE_READ         | `AFTER_PAGE_READ`         | After each page has been read and been parsed by Mistune for content and metadata. Passes context and the page as arguments. |
| AFTER_ALL_ARTICLES_READ | `AFTER_ALL_ARTICLES_READ` | After all articles have been read and been parsed by Mistune for content and metadata. Passes context and the list of articles as arguments. |
| BEFORE_WRITING          | `BEFORE_WRITING`          | After all content is scanned and parsed, before anything is written. Passes context and Writer class as arguments. |
| BEFORE_ARTICLE_WRITE    | `BEFORE_ARTICLE_WRITE`    | Before each article is written. Passes context and article object as arguments. |

### Caching for plugins

If your plugin introduces a new file type (in addition to articles, pages and indexes), maybe author pages listing articles by particular authors, then it can make use of Olm's caching. The file should be a class that inherits from the `Source` class in `olm.source`.

The file should have the attribute `cache_type` set to some unique value. In the author page example maybe you would choose `AUTHOR_PAGE`. All these files should be added to the all_files object in the context before the caching functions are run. They will then be hashed like the articles and pages and given the `same_as_cache` attribute indicating if they have changed.

If one of these file types changes it will appear in the changes list too so you can have indexes, articles, pages or anything else you add rewritten when the file changes. In the author example it would be added as `AUTHOR_PAGE.METADATA` or `AUTHOR_PAGE.CONTENT` depending on what changed.

## Acknowledgement

Heavily inspired by the [Pelican](https://blog.getpelican.com/) static site generator.
