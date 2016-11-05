Not Persistent Fields
=====================

By default, all the fields defined in a Module are made persistent into the database, but there are some exceptions.

Transient Fields
----------------
In the fields section, a field can be defined as TRANSIENT (NOTE : the naming convenition is use lowercase for that field)

    "fields" : [
      {
        "name" : "numSupporters",
        "type" : "Integer",
        "transient": true
      },
      ...
    ]

In this case the "consequences" are:
* A getXXX() and setXX() methods are generated
* The field is NOT created in the database
* Those fields are validated 

Temporal Fields
---------------
If in the fields attribute of an action we refer a field name that does NOT exist in the module's field, this field is marked for this action as TEMPORAL (NOTE : the naming convenition is use lowercase for that field)

    "fields" : [
      {
        "name" : "Name",
        "type" : "String",
      },
      {
        "name" : "numSupporters",
        "type" : "Integer",
        "transient": true
      }
    ],
    "actions" : [
      {
        "name" : "AddAll",
        "type" : "add",
        "fields" : [
           { "name" : "Name" },
           { "name" : "numSupporters" },
           { "name" : "age" }
        ]
      }
    ]   

In this example 'age' is a TEMPORARY field, that means:
* There are NO getXXX() and setXX() methods
* The field is NOT created in the database
* Those fields are validated 

So, they are very similar to the TRANSIENT but with the difference that they are used only in the action's scope, the do not appear in the Entity.
