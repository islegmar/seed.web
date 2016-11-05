# Project structure

If a project uses seed.web, a certain directory structure is used.

    <PRJ_HOME>
    |- model/
    |  |- *.json
    |  |- custom/
    |  |- data/
    |  |- testSqlFiles/
    |
    |- build   
       |- fe/
       |  |- module1/
       |  ...
       |- be/
          |- module1/
          ...

# Mini-FAQ

## How are the templates organized?

Component / Part / Technology

    ├── Module                   
    │   ├── BE                   
    │   │   └── PHP     base module's BE developed using PHP         
    │   └── FE                   
    │       └── SOOCSS  base module's FE developed using HTML (SOOCSS) 
    └── Web                      
        ├── BE                   
        │   └── PHP     base web's BE developed using PHP
        └── FE                   
            └── SOOCSS  base web's FE developed using HTML (SOOCSS)

    FE : Front end
    BE : Back end


# Startup

## Startup 'anxious mode'

## Startup 'coffe-break mode'

# Samples of use

## Create a web application for CRUD one table
This allows to generate files based on a certain template.
In this case, it will be used to generate PHPModules (with the persistance bean, views, list,....)

Some uses:

Generate for me a PHPModule

    python genModule.py -t templates/PHPModule test

    Help
    ====
    usage: genModule.py [-h] [-t TEMPLATE] [-d DESTINATION] [-r RESOLVER] [-c CFG]
                        [-k KEYS] [-i]
                        name

    Generates a module using template.

    positional arguments:
      name                  The name of the generate module

    optional arguments:
      -h, --help            show this help message and exit
      -t TEMPLATE, --template TEMPLATE
                            The folder containing the template be used
      -d DESTINATION, --destination DESTINATION
                            The folder where the module will be generated
      -r RESOLVER, --resolver RESOLVER
                            Resolver to be used
      -c CFG, --cfg CFG     File with the config file. If not specified, the file
                            ./[moduleName].json
      -k KEYS, --keys KEYS  Comma separated with the attribute names ordered when
                            printing as html
      -i, --info            Print a html with the ingo in the config file

----

    {
      "fields" : [
        {
          "name" : ...
          "type" : "String|Word|Password|Email|Object|Integer|FK|ParentK?|Bool|File|Image" 
          "nullable" : true|false (2) => Validation rule in the BE and used also in the SQL
          "unique" : true|false => If true, add a validation in the BE and constraint in the SQL
          "repeat" : true|false => If true, in the UI a repeat element is shown and a JSON is stored in the database
          "doHash" : true|false => If true, the FE send hash to the BE
          "chooseFromList" : only for FK? Def. is true, if false, this is a hidden value 
          "hide" : true|false
          "readOnly" : true|false
          "required" : true|false
          "values" : list of possible values (can be used for String, Integer,...)
          "config" : {
            "<type>" : {
              // Extra config parameters depending on the data type:
              - String
                + "max_len"
              - Integer:
                + default
              - FK
                + "url"
                + "className"
                + "fieldName"
                + chooseFromList????
            }
          }
        } 
      ],
      "actions" : [
        {
          "name" : ....
          "type" : "add|mod|list|view|other"
          "onlyOwnerCanModify" : true|false
          "fields" : [ .... ]
          # Any action has a serie of params.
          # Those param's values come in the request parameters.
          # It is a collection of fields in the form
          # { "name" : "..." } 
          # The action of params depends on the type of action:
          # - list : acts as a filter, adding a WHERE condition using those fields  
          # - add/mod : set the value for a certain field (fex. when adding a child set
          # the value for the parent's id)
          # - del : no found a use yet
          # - other : it decides
          # @TODO : Those params could be optional or not (fex. adding an attribute)
          # but now they are non optional.
          "params" : [ => Optional Element
            { 
              "name",
              "operator" : [>|<|...] Optional. Only used in the list. 
                           If not specified 'LIKE' is used
              "value" : If starts wit $ means the value is obtained from a 
                        request parameter. If not, it is a literal.
            },
            ...  
          ]

          "globalActions" : [
            {
              "module" : the module's name
              "name" : the action's name
              // OLD 
              "map" : [ => Optional element
                {
                  "key" : ... => The parameter name when calling the action
                  "value" : ... => The value assigned to the parameter
                }
              ]
              // NEW
              "params" : [ => Optional element
                {
                  "name" : ... => The parameter name when calling the action
                  "value" : ... => The value assigned to the parameter
                }
              ]







            }
          ],
          "itemActions" : [
            // Same data that with globalActions
          ],
          // Only apply in 'list'. There are two possible scenarios:
          // - Static filter : value must be set and not empty. 
          //   When building the static query to return the list, that will be filtered 
          //   using that value.
          //   Fex. if filter is { "name" : "Age", "operator" : ">", "value" : 18 }
          //   that means the query will contain "AND Age > 18"
          // - Dynamic filter : value not set or empty
          //   When building the query the values in the request will be used
          //   Fex. if filter is { "name" : "Age", "operator" : ">" }
          //   If when invoking the list we pass the parameter ....?Age=12, then the query 
          //   will contain "AND Age > 12". If no value is passed @TODO : ignore or exception?
          "filter" : [ 
            {
              "name" : ...
              "operator" : >|<|=|....
              "value" : ...
            }
          ]
        }
      ],
      "importers" : [
        {
          "name" : "" -> FactoryObjects
          "fields" : [
            {
              "transform" : "" -> FactoryObject
              "indexes" :  [ {"ind" : 0}, ... ],
              "config" : {
                Config depend on the transform used (fex. dateFormat, 
                table+field for FK,...)
              }        
            }
            ....
          ]
        }
        ...
      ]
    }

lists and filters
-----------------

How are used 'globalActions' and 'itemActions'?
-----------------------------------------------
+ lists : 
  - itemActions : for every item in the list. 
    - If no 'map' is specified, the action receives the attribute Id (if action 
      is in the same module) or Id<Module> (if action is in another module). 
    - If 'map' is specified, the action will receive a serie of parameters    
  - globalActions : in the bottom in the list.

# Templates Implementations

## Front-End (FE)

### SOOCSS

#### Upload Files

**Web/FE/SOOCSS/include/internal/js/jquery.jsonform.js**

Upload a File
    
    function uploadOneFile(fileContents, $file, file, onDone) {
      $.post(
          options.url2UploadFiles, =====> USE THE PARAMETER 'url2UploadFiles'
          { 
            content : fileContents,
            name    : file.name,
            size    : file.size,
            type    : file.type
          },
          // The file has been uploaded into the server
          function(data) {
            // Add this info returned from the server (basically the URL),
            // so when we create the JSON object we can use it as data value
            $file.data('jsonform-file', data); ====> SET DATA ATTRIBUTE 'jsonform-file'
            onDone();
          }
      );
      
    }

Set the field value after submitting the File

    function fillValues($container, data, encodeValues) {

      if ( $ele.attr('type')=='file' ) {
        if ( options.debug ) console.log('FILE : ' + $ele.val());
        if ( $ele.data('jsonform-file') ) {
          fieldValue = $ele.data('jsonform-file').url;  ==> USE THE 'url' VALUE
          $ele.removeData('jsonform-file');
        // Si no existe 'jsonform-file' quiere decir que dejamos el fichero 
        // que había antes. En este caso, el valor se habrá guardado en 
        // $field.data('jsonrender-file', value);
        // @todo : unificar  
        } else {
          if ( $ele.data('jsonrender-file') ) { 
            fieldValue = $ele.data('jsonrender-file');
          }
        }
      }
    }

**Module/FE/SOOCSS/{ActionName}{MODULE}.html.[mod|add].tmpl** 

    $.getJSON(
      "{urlBE(/service/{MODULE}/service/Load{MODULE})}",
      { 'Id' : getUrlParams()['Id'] }, 
      function(data) {
        ....
        form.jsonform({
          ....
          'url2UploadFiles' : '{urlBE(/service/UploadFile)}',
          ....
        });
      }
    );
    
## Back-End (BE)

### PHP

#### Upload Files
