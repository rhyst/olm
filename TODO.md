# TODO

* [ ] Static files  
    - [x] SASS/SCSS compilation
    - [x] JS minification?
    - [ ] Allow ES6/Typescript?
* [ ] Plugins    
    - [x] Implement callbacks for plugin style things to run
    - [x] Plugins should be added to path so they can use relative import
    - [ ] More plugin callbacks
* [ ] Content
    - [x] Pages
    - [x] Index
    - [ ] Implement authors
    - [ ] Index only content
    - [x] Subsites
        * [x] Subsites compiled into own directory
        * [x] Subsite has own settings
        * [x] Subsite has own themes (inherit from main where possible)
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
        * [x] Statics folders
        * [ ] Statics processing options