# Olm

An olm is a cave dwelling amphibian that I imagine is fairly static. This is a fast, featureful, static site generator.

VERY WIP.

## Install

## Run

## Content

## Themes

## Plugins

Plugins can subscribe to signals to modify data during the build process. The plugin should be in the plugins folder with a directory and python file with the same name: 

```
.
├── src
├── dist
├── theme
└── plugins
    └── mycoolplugin
        └── mycoolplugin.py
```

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
AFTER_ARTICLE_READ |`AFTER_ARTICLE_READ` | After each article has been read and been parsed by Mistune for content and metadata. Passes the article as the single argument.

## Acknowledgement

Heavily inspired by the [Pelican](https://blog.getpelican.com/) static site generator.
