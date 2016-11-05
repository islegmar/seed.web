Model files
===========

The most important element in seed.web are the model files, the JSON files (located under `$PRJ_HOME/model/') that describe the metadata for every entity in a language neutral way. 

File structure
--------------

Following the generic structure:

    {
      "fields" : Array of field definitions,
      "transformer" : File importer definition,
      "actions" : Array of actions
    } 

and with a little more details:

    {
      "fields" : [
        {
          "name" : ...

        },
          ....
      ],
      "transformer" : File importer definition,
      "actions" : Array of actions
    } 

Fields
----------

### FK (Foreign Keys)

By default, in the FE a dropdown is shown in order to select an item. For example if we have configures

    {                                          
      "name" : "Id_Lang",                         
      "type" : "FK",                           
      "config" : {
        "FK" : {
          "module"  : "_Lang",
          "actionName"  : "ListAll",
          "fieldName" : "Locale",
          "relationType" : "aggregation"
        }
      }
    }

when rendering the field Id_Lang, a dropdown is built containing the result of executing the action ListAll of the module _Lang and from the returned info the field Locale is shown.

*What if for a certain action I do NOT want to show all the items*

Let's suppose thast for a certain action you do not want to show all the _Lang but a filter of them (ex. the Ones with a certain Orientation).

This is a 2 step process:

+Step1+     
Create the List that receives a parameter

Following our example we have to add the action _Lang:ListByOrientation, so we will add the following in the _Lang.json


    {
      "name": "ListByOrientation",
      "type": "list",
      "params" : [
        { "name" : "Orientation" }
      ]
    }

+Step2+
Use this action when configuring the FK

Let's suppose in another page we want to show the field Id_Lang but instead showing all the possibles languages (ListAll) we want to use only those with a certain orientation (ListByOrientation) where the Orientation value is passed in the request.

As an example, we will add the field Id_Lang to _User and we will show a list with all the Users where we can filter by lang, but only with a certain orientation.

    _User.json

    "fields" : [
      ...
      {                                          
        "name" : "Id_Lang",
        "type" : "FK",            
        "config" : {
          "FK" : {
            "module"  : "_Lang",
            "actionName"  : "ListAll",
            "fieldName" : "Locale"
          }
        }
      }
      ...
    ],
    "action" : [
      ...
      {
        "name": "MyList",
        "type": "list",
        "fields" : [
          { "name" : "Login"   },
          { 
            "name" : "Id_Lang",
            "actionName"  : "ListByOrientation",
            "params" : [
              { "name" : "Orientation", "value" : "$Orientation" }
            ]
          } 
        ]
      }
      ...
    ]

Now, if we show the page MyList passing the parameter Orientation (/fe/_User/MyList_User.html?Orientation=RTL) what we will get is a list of all the users but in the search filter, if the field Lang ONLY the langs with the Orientation RTL are shown.

Some comments:

* The "fields" we have specified in the action are the fields we shown in the list BUT also are used to build the search form UNLESS we have defined the parameter "listFilter".

* When using the field "Id_Lang" in the action MyList, the configuration defined in "fields" and used and then we overwrite some of the parameters defined in the action. That means the configuration of Id_Lang in the action is:


The initial in "fields"

>      {                                          
>        "name" : "Id_Lang",
>        "type" : "FK",            
>        "config" : {
>          "FK" : {
>            "module"  : "_Lang",
>            "actionName"  : "ListAll",
>            "fieldName" : "Locale"
>          }
>        }
>      }

This is equivalent (normalized) to:

>      {                                          
>        "name" : "Id_Lang",
>        "type" : "FK",            
>        "module"  : "_Lang",
>        "actionName"  : "ListAll",
>        "fieldName" : "Locale"
>      }

And finally the configuration of the field in the action is

>      {                                          
>        "name" : "Id_Lang",
>        "type" : "FK",            
>        "module"  : "_Lang",
>        "actionName"  : "ListByOrientation",
>        "fieldName" : "Locale"
>        "params" : [
>          { "name" : "Orientation", "value" : "$Orientation" }
>        ]
>      }

* When building the list's contents Id_Lang's parameters as actionName is ignored

## Date/DateTime

When using fields of type Date we MUST add a new attribute "time" in the format HH:mm:ss to indicate with which time we are going to keep this date, otherwise it is stored in the specified date BUT the current time, make it impossible make comparation.

Example

    {
      "name": "Start",
      "type":"Date",
      "format": "dd/MM/yy",
      "time" : "00:00:00"
    },
    {
      "name": "End",
      "type":"Date",
      "format": "dd/MM/yy",
      "time" : "23:59:59"
    }

In this example, when we store End=27/01/1932 in fact we will keep in the database unix_time('27/01/1932 23:59:29')

If a Date field appears in a filter we MUST indicate the coparator that will be used in the query

    {
      "name": "ListAll",
      "type": "list",
      "listFilter" : [
        { "name" : "Login"   },
        { "name" : "Start", "operator" : ">=" },
        { "name" : "End", "operator" : "<=" }
      ]
    }

In this example, if we set the value End=20/09/1924 the query will be

    AND End <= unix_time('20/09/1924 23:59:59')

Actions
-------

    "actions" : [
      {
        // The action's name, used when generating the file's names, permissions,...
        "name" : "String"

        // The action's type
        "type" : "add|mod|list|view|chart|import|load|dashboard|composed|other"
        
        // Optional (default:false)
        // If true, only the owner of this record can upddate it
        // @TODO : review, make it more generic, not only for update and not 100%
        // sure if it is working
        "onlyOwnerCanModify" : true|false,

        // Optional (default:ModuleName:ActionName)
        "permission" : "String" 

        // Optional (default:false) 
        // If true, the FE code (if any) is NOT generated
        "beOnly" : true|false 

        // Optional (default:false) 
        // If true, the BE code (if any) is NOT generated
        "feOnly" : true|false 

        // Optional (default:false) 
        // If true, in the FE a confirmation message is shown before the BE 
        // action part of the code is executed
        "askConfirmation" : true|false +
        
        // Optional (default: list of fields defined for this entity in the
        // roog "fields" section, see above)
        // Used only for the list action. 
        "fields" : [ 

        ],

        // Optional (default: the list of fields defined in fields)
        // Used only in the actions of type:list and it is the list of fields
        // that are shown in the filter form. If we do NOT what to have a filter
        // for a certain list you have to use
        // "listFilter" : []
        "listFilter" : [

        ]

        // Optional (default: none)
        // Aray of params that this action expect to receive. That means that
        // when calling this action (see globalActions of )
        "params" : [
          { 
            "name" : "String"
            "operator" : [>|<|...] Optional. Only used in the list. 
                         If not specified 'LIKE' is used
            "value" : If starts wit $ means the value is obtained from a 
                      request parameter. If not, it is a literal.
          },
          ...  
        ]
  
        // Optional (default: none)
        "globalActions" : [
          {
            "module" : the module's name
            "name" : the action's name
            "params" : [ => Optional element
              {
                "name" : ... => The parameter name when calling the action
                "value" : ... => The value assigned to the parameter
              }
            ]
          }
        ]

        // Optional (default:???)
        // @TODO : review it
        "loadDataURL" : "???"

        // Optional (default : none)
        // Only used in 'list'
        // List of field names in the order by 
        // If direcc is not specified, ASC is the default
        "orderBy" : [
          { "name" : "fieldName" [, "direcc" : "ASC|DESC"]},
          ....
        ]

        // Optional (default: execute the acion ViewAll for this record)
        // Only used in 'list'.
        // Action performed when clicking on a list record. If we want disable 
        // this feature (so, no action is performed when clicking) use
        // "onClick" : null  
        "onClick" : {
          "module" : "The module where the action is located",                           
          "actionName" : "The action's name",
          // Optional : the params' values needed for this action                   
          "params" : [                                  
            { "name" : "...", "value" : "..." }
            ...     
          ]                                             
        }

        // [list] Optional (default : none)
        // It has the same structure than "globalActions" and are the actions
        // than can be performed for every list item. They are rendered as buttons
        // in the list under a column "actions" OR out of the list  
        "itemActions" : [
          // For every action there is a new attribute called "style" that can
          // have theh values
          // + onrow : (default) the actions are shown as buttons in the same row
          //           under the column 'actions'
          // + outrow : the actions are shown as buttons out of the table. That
          //            means that in order to know to which single element we're
          //            going to perform the action (remember, tjose are itemActions
          //            not globalActions), we have to select before the row
          //            clicking in the radio button under the column _itemSelector)
        
          // EXAMPLE:
          {
            "name": "ListAll",
            "type": "list",
            "fields" : [
              { "name" : "Login"   },
              { "name" : "Id_Role" },
              { "name" : "Email" },
              { "name" : "Id_UserStatus" } 
            ],
            "itemActions" : [
              {
                "module" : "_User",
                "name" : "DelAll",
                "style" : "outrow",
                "params" : [
                  { "name" : "Id", "value" : "$Id" }
                ]
              },
              {
                "module" : "_User",
                "name" : "ModAll",
                "style" : "outrow",
                "params" : [
                  { "name" : "Id", "value" : "$Id" }
                ]
              }
            ]
          }
          // END EXAMPLE
        ]
        
        // Optional (default : none)
        // Only used in 'composed' and 'dashboard.
        "sections" : [
        ]

        // Optional (default:none)
        // Only used in 'chart'
        // @TODO : review
        // Sql used to generate the chart
        "sql" : "String"

        // Optional (default:refresh)
        // The action that is performed in the FE after a certain action is done:
        // + back : history.back()
        // + refresh : refresh the current page
        // @TODO : actually it has been tested only in the 'del' action
        "goOnActionDone" : "back|refresh"
      },
      ...
    ]

### Importer

When importing data, a GENERATED service is called:

    /be/service/<Entity>/service/Import<Entity>

The class hierarchy is the following:

        Service
           ^
           |    
         ETLSrv (abstract) : call the Extractor / Transformer / Loader
           ^
           |    
    ETLCSVExtractorSrv (abstract) : set ExtractorCSV as extractor (parse CSV file)
           ^
           |    
    _Import<Entity>Srv (generated) : configure Transformer / Loader based on the JSON
           ^
           |
    Import<Entity>Srv    

In general, the process is:

    Extractor [provides data] ----> Transform [transform data] ----> Loader [stores data]

The current implementation it is not a full ETL because some things are 'hardcoded' :

* **E**xtractor : always parses a CSV file . It returns `List<String>`
* **T**ransformer : this is configurable. It returns `Map<String,Object>`
* **L**oader : always create and Entity and keep in the database

Let's take a closer look to the different classes

**ETLSrv**

This is a generic abstract class. Obtains instances of the Extractor / Transformer / Loader an process all the input data processing in loop: 

The current implementation is:

    public function perform() {
      $extractor = $this->getExtractor();
      $transformer = $this->getTransformer();
      $loader = $this->getLoader();
  
      // @TODO : allow chunks!
      $tot=0;
      while ( !is_null($data=$extractor->extact())) {
        $loader->load($transformer->transform($data));
        ++$tot;
      }
  
      return array (
        'totRecords' => $tot
      );
    }

**ETLCSVExtractorSrv.php**

This abstract class 'fix' the **Extractor**. It reads the contents from the uploaded file (a CSV) and for every line it will return all the fields splitted together with the request parameters to the service (those params are defined in the JSON). The data is returned as map where the key can be:

* Numeric : line's split
* Not Numeric : the service's request parameter

So, if the line contains

    123|John Doe

and the service was called with the request parameters

    electionId=999

then the data retured by the extractor is:

    {
      0 : "123",
      1 : "John Doe",
      "electionId" : "999"
    }        


**_Import<Entity>Srv**

This is the generated code. It receives the config data coming from the JSON and it 'fixes' the **Transformer** and the **Loader**. 

It receives a configuration like:

  ,"transformer" : {
    "fields" : [
      {
        "name" : "Name", 
        "indexes" : [ { "index" : 0 } ], 
        "transformer" : "TransformString"
      },
      {
        "name" : "Orden", 
        "indexes" : [ { "index" : 1 }, { "index" : "electionId"} ], 
        "transformer" : "MyTransform"
      }
    }

The fist step is performed by the Transformer (etl/Transformer.php). Based on the Map received by Extractor, it generates another Map where the key is the fieldName and the value is a single value or a list of values based on the indexes and the information returned by the Extractor. In this example, it will generate something like:

    {
      "Name" : apply TransformString on the value with index '0' (123),
      "Orden" : apply MyTransform on the values with indexes '1' and 'electionId' [ 'John Doe', '999']
    }     

The the Loader is called. In this case, it will instrantiate Entity , call the setXXX() and will create in the database.