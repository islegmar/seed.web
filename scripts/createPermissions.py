#!/usr/bin/python
import os
import argparse

#  -----------------------------------------------------------------------------
# Generates the SQL with all the permissions
#  -----------------------------------------------------------------------------


# ==============================================================================
# Main
# ==============================================================================
def main(fields):
  print """{
  "fields" : ["""

  listFields = enumerate(fields)
  for idx, field in listFields:
    sep = "," if idx>0 else ""
    if field.lower() == "id":
      field="__id"
    elif field.lower() == "idowner":
      field="__idOwner"

    print """    {sep}{{ 
      "name" : "{field}", 
      "type" : "String", 
      "config" : {{
        "String" : {{
          "max_len" : 128
        }}
      }}
    }}""".format(**locals())


  print "  ],"

  # transformer
  print """  "transformer" : {
    "fields" : ["""


  for idx, field in enumerate(fields):
    sep = "," if idx>0 else ""

    print """      {sep}{{ 
        "name" : "{field}", 
        "indexes" : [ {{ "index" : {idx} }} ],
        "transformer" : "TransformString"
      }}""".format(**locals())

  print """    ]
  },
  "actions" : [    
    {                                                                  
      "name" : "ListAll",                                              
      "type" : "list",                                                 
      "fields" : ["""
  for idx, field in enumerate(fields):
    sep = "," if idx>0 else ""

    print '        {sep}{{"name" : "{field}"}}'.format(**locals())

  print """      ],
      "itemActions" : [                                                
      ],                                                               
      "filter" : [                                                     
      ]                                                                
    }                                                                  
  ]
}"""

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generates the SQL with all the permissions')
  parser.add_argument('fields', nargs='*', help='The generated i18n file')

  args = parser.parse_args()
  
  main(args.fields)