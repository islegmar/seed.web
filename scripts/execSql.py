#!/usr/bin/python
import os
import argparse

#  -----------------------------------------------------------------------------
# Contains all the functionalities related with actions in the database:
# - Create the projects database
# - Creeate a certain module's table
#  -----------------------------------------------------------------------------

# ==============================================================================
# Functions
# ==============================================================================
def run_sql_file(self,fSql, pUser, pPwd, pDb, pHost='localhost', pPort=3306):
  createMySQLDB(MYSQL_DB, MYSQL_USR, MYSQL_PWD, MYSQL_SERVER, MYSQL_PORT, MYSQLROOT_USR, MYSQLROOT_PWD)
  user = pUser if pUser else os.environ['PRJ_NAME']
  pwd  = pPwd  if pPwd  else os.environ['PRJ_NAME']
  



  mysql_exe=os.environ['MYSQL_EXE']
  cmd="{mysql_exe} --user={user} --password={pwd} --host={host} --port={port} {db} < {fSql} 2>&1|grep -v '^Warning:'".format(**locals())
  exec_cmd(cmd)   

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
  parser = argparse.ArgumentParser(description='Generates a config file')
  parser.add_argument('fields', nargs='*', help='The generated i18n file')

  args = parser.parse_args()
  
  main(args.fields)