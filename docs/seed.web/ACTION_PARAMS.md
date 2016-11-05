Action Params
=============

Every action is a widget
Every widget when rendering receives the array widgetData[] componed by:

* All the URL params
* In the object 'User' all the data related with the current user
* In the object 'actionParams' all the params defined for taht action and as the values resolved using... widgetData, that in this case is the same as the URL params.

Let's suppose we have an action for _User as ViewAll, defined as

    {
      "_desc" : "DEFAULT : View",
      "name" : "ViewAll",                                              
      "type" : "view",
      "params" : [
        { "name" : "Id" }
      ]                                                              
    }

That is, this action requires a parameter 'Id'

Now, if we call the following URL

    /_User/ViewAll_User.html?Id=1&name=John

widgetData will contain:

    {
      "Id":"12",
      "name":"John",
      "User": {
        // logged user serialized...
      },
      "actionParams": {
        "Id":"1"
      }
    }

Next question, once we have widgetData with all this bunch of data, where is it used? It is used in a lot of places, depending on the action type:

* In a view/add/mod action, when loading data from the server (for the add action could be just for retrieve some default values), a Load action need to be called     




    {
      "roleId":"1",
      "User": {
        // logged user serialized...
      }
    }
