FE : SOOCSS
===========

NOTE : during the following widget and action is sometimes used interchangeably. If we are purist, action is the global, and some actions are rendered as widgets (with UI). 

How is the page content organized?
----------------------------------

The page contains a serie of WIDGETS, each of them identified with a unique ID. Usually a page contains a single widget, but if the template composed is used, it can contain several.

Let's see an example of page containing ONE widget. It seems complex but it is needed when we compose several widgets in a single page (see below),

    <html>                                                                         ||
      <head>                                                                       ||
        .....                                                                      ||
      </head>                                                                      ||
      <body>                                                                       ||-> _start.inc
        <div class="page-wrapper">                                                 ||
          <header with the user info, choose lang,.../>                            ||
          <div class="container demos">                                            ||
            <div #pMsgOK/>  (1)                                                    ||


            <div id="<THIS_WIDGET_ID>">  (2)                                       ||
              <script>                                                             ||
              - Waits for the custom.ready event                                   ||
                  $(document).on('custom.ready', function(evt, usr)                ||
              - Once received:                                                     ||
                - Check the user permission (every widget has different ones)      || -> _startWidget.inc
                  - NO has permission : the HTML contents is hidden and an         || 
                    error message is shown                                         ||
                  - YES has permission : a trigger is thrown to this widget ONLY   ||
                      $('#<THIS_WIDGET_ID>').trigger("custom.widgetReady", [usr]); || 
                                                                                   ||
              </script>                                                            ||
              <div class="_widgetContent">                                         ||


                - HTML specific for the widget (list, view, add, mod,....)  (3)
                - It waits until THIS widget receives the custom.widgetReady event 
                    $('#<THIS_WIDGET_ID>').on("custom.widgetReady", function(evt, usr){
                - Once received, the widget can start its job (requesting info to the server,...)
                - If in the HTML we must identify a unique element, we can use expressions like
                    $('#<THIS_WIDGET_ID> relative_path_using_classes')   
              

              </div>                                                            ||-> _endWidget.inc
            </div>                                                              ||


          </div> <!-- /container -->                                            ||
        </div> <!-- /page-wrapper -->                                           ||
        <footer with the company info>                                          ||
        <script>                                                                ||
          - Display the msg OK (if any)                                         ||
          - Request to the server for the I18N                                  ||
          - Request to the server for the current user                          || -> _end.inc
          - If everything is ok, trigger an event custom.ready that will be     ||
            catch for EVERY widget                                              ||
              $(document).trigger( "custom.ready", [ user ] );                  ||
        </script>                                                               ||
      </body>                                                                   ||
    </html>                                                                     ||

(1) Only ONE msgOK is shown per page

(2) In case several widgets are in the same page, each of them has a UNIQUE id.

(3) Should all the widgets have a coommon HTML elements? Like

* Title
* Error Message Box
* Global Actions ===> Nice to have?

In case we use the template 'composed', the widgets are grouped in sections.

Let's suppose the following configuration

    {
      "_desc" : "For the admin, show an overview of the Elecction, including Candidates and Supporters",
      "name" : "ViewFull",    
      "type": "composed",
      "sections" : [
        {
          "actions" : [
            {
              "actionName" : "ViewElection",
              "module" : "Election",
              "name" : "ViewAll",
              "params" : [
                { "name" : "Id" , "value" : "$Id" }
              ]
            }
          ]
        },
        {
          "actions" : [
            {
              "actionName" : "ListCandidates",
              "module" : "Candidate",
              "name" : "ListByElection",
              "params" : [
                { "name" : "IdElection" , "value" : "$Id" }
              ]
            },
            {
              "actionName" : "ChartCandidates",
              "module" : "Candidate",
              "name" : "ListByElectionGroupByCandidateStatus",
              "params" : [
                { "name" : "IdElection" , "value" : "$Id" }
              ]
            }
          ]
        },
        {
          "actions" : [
            {
              "actionName" : "ListSupporters",
              "module" : "Supporter",
              "name" : "ListByElection",
              "params" : [
                { "name" : "IdElection" , "value" : "$Id" }
              ]
            }
          ]
        }
      ]                             
    }

This view has 3 sections (3 rows).

* First section : contains one widget (Election:ViewAll) that will take the 100% width.
* Second section : contains two widgets (Candidate:ListByElection and Candidate:ListByElectionGroupByCandidateStatus) each of them taking 50% width.
* Third section : contains one widget (Supporter:ListByElection) that will take the 100% width.

Now, let's take a look to the generated HTML:

    .....                               || 
    <div class="container demos">       || ---> _start.inc
      <div #pMsgOK/>                    ||
      
      <div class="flex-container h-100">            ||
        <div class="flex-item w-100 w-sm-100">      ||
          [_startWidget.inc] (id="Widget1")         ||         
            HTML + JS for Election:ViewAll          || ---> Section
          [_endWidget.inc]                          ||
        </div>                                      ||
      </div>                                        ||

      <div class="flex-container h-100">
        <div class="flex-item w-100 w-sm-50">
          [_startWidget.inc] (id="Widget2")
            HTML + JS for Candidate:ListByElection
          [_endWidget.inc]
        </div>
        <div class="flex-item w-100 w-sm-50">
          [_startWidget.inc] (id="Widget3")
            HTML + JS for Candidate:ListByElectionGroupByCandidateStatus
          [_endWidget.inc]
        </div>
      </div>

      <div class="flex-container h-100">
        <div class="flex-item w-100 w-sm-50">
          [_startWidget.inc] (id="Widget4")
            HTML + JS for Supporter:ListByElection
          [_endWidget.inc]
        </div>
      </div>
    
    </div>          || --->_end.inc
    ....            ||

Some comments:

* The entire page has a unique instance of _start.inc and _end.inc.
* There is only one pMsgOK per page (but each widget has its own pMsgError)
* The 'composed' it is NOT a widget, it is not surrounded by _startWidget.inc / _endWidget.inc
* Each widget has its own WIDGET_ID
* Each SECTION is surrounded by a   

    `<div class="flex-container h-100"> ... </div>`

* Each WIDGET inside a section is surrounded by a 

    `<div class="flex-item w-100 w-sm-<WIDGET_WIDTH>"> ... </div>`

  where WIDGET_WIDTH is variable and depends the number of widgets in the section (100, 50, 33, ...)  

Widget data
-----------

As we have seen, when a widget is rendered (after checking the user permissions), it receives some global data:

* User with the info of the connected user (also in case it is a non authenticated user)
* TODO : receive the request params
* TODO : receive some global applications configuration (coming from _ConfigAp) ---> not sure about taht

Then, each widget can receive aditional data requested from the server. For example in a 'mod' widget, it will receive the data of the item we are going to update (well, in fact we SHOULD receive only the fields configured to be processed by this action *TODO*: check if this is the case)

That means, in the context of a widget it has access to:
* User
* Request
* _ConfigApp?
* Specific data

All this data is stored in a javascript variable 'widgetData' (one per widget) and the info there contained can be referenced in the JSON files as `$<varName>`.

Widget params, widget data, .....
---------------------------------

When configuring any action, it has an attribute 'params'. Let's suppose the module "MyModule" defines the following action

    "action" : {
      "name" : "MyAction",
      "params" : [
        { "name" : "Param1" },
        { "name" : "Param2" }
      ]
      ....
    }

When an action is refered from another action the values for such params must be provided. Let's suppose the module "OtherModule" defines the action "OtherAction" and from there a link to the action previously defined. 

    "action" : {
      "name" : "OtherAction",
      "globalActions" : [
        "module" : "MyModule",
        "name" : "MyAction"
        "params" : [
          { "name" : "Param1", "value" : "$Id" },
          { "name" : "Param2", "value" : "22"  }
        ]
      ]
      ....
    }

Then, when the link to MyAction is build, the URL contains two params:

* Param1 : value is widgetData['Id']
* Param2 : value is the literal "22"

So, we can provide literal or variable data and in the second case the variable is extrated from widgetData.

Actually, the actions are referred in the following places

* "globalActions" inside an action.
* In the composed pages
* In the dashboard (review)

Chain of actions
----------------

Let's suppose we have a composed page with some widgets, each of them referring other widgtes:

    MODULE : Election

    {
      "name" : "ViewFull",    
      "type": "composed",
      "sections" : [
        {
          "actions" : [
            {
              "actionName" : "ViewElection",
              "module" : "Election",
              "name" : "ViewAll",
              "params" : [
                { "name" : "Id" , "value" : "$Id" }
              ]
            },
            {
              "actionName" : "ListCandidates",
              "module" : "Candidate",
              "name" : "ListByElection",
              "params" : [
                { "name" : "IdElection" , "value" : "$Id" }
              ]
            }
          ]
        }
      ]              
    }

So, the composed page Election:ViewFull contains:
* Election:ViewAll : for a certain Election, show the details. 
* Candidate:ListByElection : for a certain Election, show the Candidates. 

If we take look to the actions's definitions
 
    MODULE : Election

    { 
      "name" : "ViewAll",                                              
      "type" : "view",
      "params" : [
        { "name" : "Id" }
      ]                                                              
    }

and 

    MODULE : Candidate

    {
      "name" : "ListByElection",                                              
      "type" : "list",                                                 
      "params" : [
        { "name" : "IdElection" }
      ]
    }

So, what we see here is that there is matching in the params:
* Election:ViewAll receives as param 'Id'
* Candidate:ListByElection receives as param 'IdElection'

And the value for those params has been provided by the container page Election:ViewFull to the contained widgets:
* Election:ViewAll : Param 'Id', Value '$Id' 
* Candidate:ListByElection : Param 'IdElection', value '$Id'

where $Id is a Election:ViewFull's param. It should be clear (and probably nicer) if we declare explicitly that Election:ViewFull has the param 'Id', something like:

 MODULE : Election

    {
      "name" : "ViewFull",    
      "type": "composed",
      "sections" : [
        {
          ...
        }
      ],                                                 
      "params" : [
        { "name" : "Id" }
      ]              
    }

*BUT* currently this is not done (and not sure how to implement it).

Until now, we see that when rendering a composed page, the contained widgets will receive the right values to their expected params but, what happens if the widgets themselves have reference to other actions that need params? We say "reference to other actions" and NOT contained actions because in the current implementations it is NOT possible to nest composed pages.

Let's take a closer look to one the contained widgets Candidate:ListByElection

    MODULE : Candidate

    {
      "name" : "ListByElection",                                              
      "type" : "list",                                                 
      "globalActions" : [
        {
          "module" : "TempCandidate",
          "name" : "Import",
          "params" : [
            { "name" : "IdElection", "value" : "$IdElection" }
          ]
        }        
      ],
      "params" : [
        { "name" : "IdElection" }
      ]
    }

As we have already seen it receives the param 'IdElection' but what is more important, it is used to provide a value to the param 'IdElection' for the action TempCandidate:Import. The fact that in this particular case the name of the param and the value are the same it is just a coincidence. It will work the same with the following configuration:

    MODULE : Candidate

    {
      "name" : "ListByElection",                                              
      "type" : "list",                                                 
      "globalActions" : [
        {
          "module" : "TempCandidate",
          "name" : "Import",
          "params" : [
            { "name" : "MyIdElection", "value" : "$IdElection" } ===> Not the same
          ]
        }        
      ],
      "params" : [
        { "name" : "IdElection" }
      ]
    }

if now the action TempCandidate:Import is configured to receive 'MyIdElection' as param, so if we have something like:

    MODULE : TempCandidate

    {
      "name": "Import",
      "type": "import",
      "params" :[
        { "name" : "MyIdElection" }
      ]
    }     

Can I add custom code in the pages?
-----------------------------------

It is possible to define custome content (mainly JS) in the generated pages? YES

Let's suppose we have defined the action 'ListAll' for the module '_User'. In order to add some custom HTML to the generated page ListAll_User.html, we have to create the file `ListAll_User.inc` in the custom folder, that is, the file ' $PRJ_HOME/model/custom/ModuleCustom/FE/SOOCSS/_User/ListAll_User.inc'. If this file exists, its content will be copied in the generated file.

Where is this content copied? This is done in *_endWidget.inc* 

      </div>
      <!-- /widgetContent -->
    </div>
    <!-- /widgetPanel -->
    {include({CustomHTML})} ==> Here the file custom content will be copied   