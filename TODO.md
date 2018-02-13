# TODO

* [ ] Static files  
    - [x] SASS/SCSS compilation
    - [x] JS minification?
    - [ ] Allow ES6/Typescript?
* [ ] Plugins    
    - [x] Implement callbacks for plugin style things to run
    - [x] Plugins should be added to path so they can use relative import
    - [ ] More plugin callbacks
    - [ ] Specify different plug path in settings 
* [ ] Content
    - [x] Pages
    - [x] Index
    - [x] Implement authors
    - [ ] Index only content
    - [x] Subsites
        * [x] Subsites compiled into own directory
        * [x] Subsite has own settings
        * [x] Subsite has own themes (inherit from main where possible)
        * [ ] Allow specifying output paths
        * [ ] Allow specifying input paths
    - [ ] Source file linking
    - [ ] More SLUGS
* [ ] Tidy
    - [ ] Import CONTEXT variable from module as needed rather than passing as parameter. Check this works with plugins.
    - [ ] Filepath helper class + standardised naming
    - [ ] Shared class for page, article, index to inherit (not sure this is necessary unless more file types are added)
* [ ] Configurability
    - [x] Add settings file
    - [x] Configurable things
        * [x] Base url
        * [x] Source and build folders
        * [x] Statics folders
        * [ ] Statics processing options
