# Olm

An olm is a cave dwelling amphibian that I imagine is fairly static. This is a fast, featureful, static site generator.

VERY WIP.

## Plugins

Plugins can subscribe to signals to modify data during the build process.

### Current signals

Signal Name | String Value | Description
---|---|---
AFTER_ARTICLE_READ |"AFTER_ARTICLE_READ" | After each article has been read and been parsed by Mistune for content and metadata. Passes the article as the single argument.
