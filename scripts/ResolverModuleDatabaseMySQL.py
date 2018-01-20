#!/usr/bin/python
# -------------------------------------------
# Resolver spedific for modules PHP
# @TODO: Do not overwrite not generate files (those that do not start with _)
# -------------------------------------------
import re
import os
import sys
import json
from ResolverModule import ResolverModule
from pprint import pprint

class ResolverModuleDatabaseMySQL(ResolverModule):

  def __init__(self, moduleName, cfgModule, options):
    ResolverModule.__init__(self, moduleName, cfgModule, options)

  # ============================================================================
  # 
  # Replacement Methods / No Templates
  # Reference to generic config as self.cfgModule['fields']
  #
  # ============================================================================

  # The drop sql have to be executed in INVERSED order than the create
  def printsqlOrderInversed(self):
    maxSqlOrder=1000000
    sqlOrder=self.cfgModule['values']['sqlOrder']

    if sqlOrder>maxSqlOrder:
      raise Exception("sqlOrder '{sqlOrder}' has a value too big, maximum expected {maxSqlOrder}!!".format(**locals()))

    return str(maxSqlOrder - sqlOrder)
      
  # -------------------------------------------
  # create{MODULE}.php
  # SQL to create the table
  # -------------------------------------------

  # {SQLFieldDecl}
  # Return all field declaration when create table
  def printSQLFieldDecl(self):
    line=""

    for varData in self.cfgModule['fields']:
      varType = varData['type']

      # The transiest fields are NOT persistent
      if varData["transient"]:
        continue

      if len(line)>0:
        line += ","
      buff=""
      if varType=="String" or varData['type']=="Word" or varData['type']=="Password":
        buff += "  {name} varchar({max_len})"
      elif varType=="NifNieCif":
        buff += "  {name} varchar(10)"
      elif varType=="Email":
        buff += "  {name} varchar(125)"
      elif varType=="URL":
        buff += "  {name} varchar(1024)"
      elif varType=="Text":
        buff += "  {name} text "
      elif varType=="Object":
        buff += "  {name} text "
      elif varType=="Integer":
        buff += "  {name} int"
      elif varType=="Float":
        buff += "  {name} float"
      elif varType=="FK" or varType=="ParentK" or varType=="File" or varType=="Image":
        buff += "  {name} int unsigned "
      # Date, store the timestamp
      elif varType=="Date" or varType=="DateTime":
        buff += "  {name} int"
      elif varType=="Bool":
        buff += "  {name} tinyint(1) "
      # @TODO : allow more config options  
      elif varType=="Binary":
        buff += "  {name} MEDIUMBLOB "
      else:
        raise Exception('Unknown data type "' + varData['type'] + '".');

      if 'required' in varData or  varData['type']=="Bool":
        buff += " not null"
      else:
        buff += " null"

      # if not varData['nullable'] or varData['type']=="Bool":
      #   buff += " not null"
      # else:
      #   buff += " null"

      # varType has been already 'normalized' with config, so this is not needed
      # if 'config' in varData and varType in varData['config']: 
      #   line += buff.format(**dict(varData,**varData['config'][varType]))+"\n"
      # else:
      #   line += buff.format(**varData)+"\n"
      line += buff.format(**varData)+"\n"

    return line

  # {FKDeclarations}
  # All the FK declarations
  def printFKDeclarations(self):
    buff=""

    for varData in self.cfgModule['fields']:
      if varData["transient"] or varData['type']!='FK':
        continue

      tableName=self.moduleName
      fieldName=varData['name']
      parentTable=varData['module']  

      # Aggregation
      if varData['relationType']=='aggregation':            
        buff += """
ALTER TABLE {tableName} ADD FOREIGN KEY ({fieldName}) REFERENCES {parentTable}(Id) ON DELETE CASCADE;""".format(**locals())
      # Association
      else:
        buff += """
ALTER TABLE {tableName} ADD FOREIGN KEY ({fieldName}) REFERENCES {parentTable}(Id);""".format(**locals())

    return buff

  # {DBFieldConstraints}
  # DB Constraints
  def printDBFieldConstraints(self):
    buff=""

    for varData in self.cfgModule['fields']:
      if varData["transient"] :
        continue

      if "unique" in varData and varData["unique"]:   
        tableName=self.moduleName
        fieldName=varData['name']

        buff +="""
ALTER TABLE {tableName} ADD CONSTRAINT uc_{fieldName} UNIQUE ({fieldName});""".format(**locals())

    return buff


  # -------------------------------------------
  # permission{MODULE}.php
  # SQL to insert the permissions for that module
  # We create the SQL for one module, but depending how the permissions are
  # configured, we can have that the same permission is used in severl amodules
  # (fex. if we create a minimalistic permission schema where all the View/Load/List
  # actions for ALL the modules have the unique permission 'Read')
  # So, we have to be sure do not iunsert duplicates.
  # -------------------------------------------
  def printModulePermissions(self):
    buff = ""

    moduleName=self.moduleName

    # All coming from the actions
    for actionCfg in self.cfgModule['actions']:
      name = self._getPermission(actionCfg, self.cfgModule, self.moduleName) 

      buff += """
INSERT INTO _Permission (Name) 
  SELECT '{name}' FROM DUAL
WHERE NOT EXISTS 
  (SELECT * FROM _Permission WHERE Name='{name}');""".format(**locals())

    return buff

  # -------------------------------------------
  # insert{MODULE}Into_Module.sql
  # Add this module's config into _Module
  # -------------------------------------------

  def printModuleConfig(self):
    # Scape single quotes
    return json.dumps(self.cfgModule).replace("'","\\'")
