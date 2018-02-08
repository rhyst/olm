# TODO

* [ ] Static files  
    - [x] SASS/SCSS compilation
    - [x] JS minification?
    - [ ] Allow ES6/Typescript?
* [ ] Plugins    
    - [x] Implement callbacks for plugin style things to run
    - [x] Plugins should be added to path so they can use relative import
    - [ ] More plugin callbacks
* [ ] Content types
    - [x] Pages
    - [x] Index
    - [ ] Index only content
    - [ ] Subsites
        * [x] Subsites compiled into own directory
        * [ ] Subsite has own settings
        * [ ] Subsite has own themes (inherit from main where possible)
* [ ] Tidy
    - [ ] Proper class for CONTEXT?
    - [ ] Make CONTEXT globally accessible?
    - [ ] Sort out filepath stuff
    - [ ] Shared class for page, article, index to inherit
* [ ] Configurability
    - [x] Add settings file
    - [x] Configurable things
        * [x] Base url
        * [x] Source and build folders
        * [ ] Statics folders
        * [ ] Statics processing options