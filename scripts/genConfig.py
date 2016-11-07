#!/usr/bin/python
# ==============================================================================
# Generates a config file based on a list of fields
#
# NOTE : I tried to generate the config serilizing the JSON, but the problem
# was there is no way to guarantee the key order, so when serializing a field
# like "name" that is expected to be generated first maybe is the last one,
# making the final JSON unreadable.
# ==============================================================================
import os
import argparse
import json
import re
import shutil
from collections import OrderedDict

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------

# Generate an array for a bunch of files EXCEPT one of them
def _listFieldsAsString(fieldsCfg, excludeFieldName=None, hideWhenExcluded=False):
  totFields=len(fieldsCfg)

  allFields = ""
  for idx, fieldCfg in enumerate(fieldsCfg):
    # sep = "," if idx<(totFields-1) else  ""
    sep = "," if len(allFields)!=0 else  ""
    name=fieldCfg['name']
    if excludeFieldName and fieldCfg['name']==excludeFieldName:
      if hideWhenExcluded:
        allFields += """
        {sep}{{ "name" : "{name}", "hide" : "true" }}""".format(**locals())
    else:
      allFields += """
        {sep}{{ "name" : "{name}" }}""".format(**locals())

  return allFields

# ------------------------------------------------------------------------------
# Generate the JSON with the import config
# ------------------------------------------------------------------------------

def _genTransformer(fieldsCfg, fieldBy=None):
  totFields = len(fieldsCfg)

  cfgTransformer = """
      "transformer" : {
        "fields" : ["""

  idx=0
  for indF, fieldCfg in enumerate(fieldsCfg):

    type=fieldCfg['type']

    # If we do a ImportBy
    if fieldBy and fieldBy==fieldCfg['name']:
      cfgTransformer += """
          {{
            "name" : "{name}",
            "indexes" : [ {{ "index" : "{name}" }} ],
            "transformer" : "TransformInteger"
          }}""".format(**dict(fieldCfg, **locals()))
    else:
      # Is a FK
      if type=='FK':
        cfgTransformer += """
          {{
            "name" : "{name}",
            "indexes" : [ {{ "index" : {idx} }} ],
            "transformer" : "TransformField2PKId",
            "config" : {{
              "beanName"  : "{module}",
              "fieldName" : "{fieldName}"
            }}
          }}""".format(**dict(fieldCfg, **locals()))
     # Is other field
      else:
        cfgTransformer += """
          {{
            "name" : "{name}",
            "indexes" : [ {{ "index" : {idx} }} ],
            "transformer" : "TransformString"
          }}""".format(idx=idx, name=fieldCfg['name'])

      idx = idx + 1

    # Add a , (except in the last)
    if indF<(totFields-1): cfgTransformer += ","

  cfgTransformer += """
        ]
      }"""

  return cfgTransformer

# --------------------------------------------------------- [_genBasicModuleCfg]
# Generates an array with all the fields configuration, taking as argument a
# list of files names that can contain all information as sata type .... based on
# certain conventions
# Also returns some config for the modules (fex. in Enumeration)
# ------------------------------------------------------------------------------

def _genBasicModuleCfg(moduleName, fields):
  fieldsCfg=[]
  # If it is dependent because if has an aggregation relation (fex. Election is
  # dependent and depends on ElectionEvent ), actions like Import / Add has no
  # sense but well the AddBy and ImportBy
  isIndependentModule = True

  # Generic file definition
  #
  #  FieldName:Type(comma_separated_args)
  #
  # where Type and comma_separated_args are optionals
  #
  #   reg=re.compile(r"(\w+)(?::(\w+)(?:\((.*)\))?)?")
  #
  # In we want to extract the comma_separated_args
  #
  #   re.findall(r'([^=]+)=([^=]+)(?:,|$)', 'foo=bar,breakfast=spam,eggs,blt=bacon,lettuce,tomato,spam=spam')
  #
  # Return a list as
  #
  #   [('foo', 'bar'), ('breakfast', 'spam,eggs'), ('blt', 'bacon,lettuce,tomato'), ('spam', 'spam')]
  #

  reField=re.compile(r"(\w+)(?::(\w+)(?:\((.*)\))?)?")
  #reArgs=re.compile(r"([^=]+)=([^=]+)(?:,|$)")

  for fieldDec in fields:
    match = reField.match(fieldDec)
    if not match:
      raise Exception("Line {fieldDec} has not have the form of field decl".format(**locals()))

    fieldName=match.group(1)
    fieldType='String' if not match.group(2) else match.group(2)
    #fieldArgs=None if not match.group(3) else reArgs.findall(match.group(3))
    fieldArgs=None if not match.group(3) else match.group(3).split(",")

    if fieldType=='FK':
      if len(fieldArgs)==3:
        fkModule=fieldArgs[0]
        fkField=fieldArgs[1]
        fkRelationType=fieldArgs[2]
        if fkRelationType!="association" and fkRelationType!="aggregation":
          raise Exception("Unknown relation type {fkRelationType}".format(**locals()))
      else:
        # if fieldName[:2]=='Id':
        #   fkModule=fieldName[2:]
        #   fkField=fieldArgs[0]
        #   fkRelationType="association"
        # else:
        raise Exception("Field {fieldName} in {fieldDec} is a FK but it NOT the format (Module, FieldName, association|aggregation)".format(**locals()))
      
      fieldsCfg.append({
        'name' : fieldName,
        'type' : fieldType,
        'module' : fkModule,
        'fieldName' : fkField,
        'relationType' : fkRelationType
      })

      if fkRelationType=="aggregation":
        isIndependentModule = False
    elif fieldType=='String':
      max_len=255 if not fieldArgs or len(fieldArgs)<1 else int(fieldArgs[0])
      fieldsCfg.append({ 'name' : fieldName, 'type' : fieldType, 'max_len' : max_len})
    else:
      fieldsCfg.append({ 'name' : fieldName, 'type' : fieldType})

  # Convention
  isEnum = len(fieldsCfg)==1 and fieldsCfg[0]['name']=='Code'
  #print "{moduleName}, enum? {isEnum}".format(**locals())

  return {
    'moduleCfg' : {
      'moduleName' : moduleName,
      'isEnum' : isEnum,
      'isIndependentModule' : isIndependentModule
    },
    'fieldsCfg' : fieldsCfg
  }

# -------------------------------------------------------------------- [_genSQL]
# Generated the SQL sentences
# ------------------------------------------------------------------------------
def _genSQL(moduleName, fullModuleCfg, file, totRecords=5):

  allSqlCfg = []

  with open(file, 'w') as pFile:
    pFile.write("DELETE FROM {moduleName};\n".format(**locals()))

  # Check if this module is a Enum. In this case we are going to generate so many
  # records as possible values

  # Generate 5 records
  for indRecord in range(1,totRecords+1):
    fieldsCfg = fullModuleCfg['fields']
    totFields = len(fieldsCfg)

    # List of fields names
    sqlFieldNames=""
    for idx,fieldCfg in enumerate(fieldsCfg):
      sqlFieldNames += fieldCfg['name']
      if idx<(totFields-1): sqlFieldNames += ","

    # List of values, together with the tables in case of FK
    # This is a progressive task
    sqlFieldValues = ""
    sqlFKJoins     = ""
    totJoins       = 0

    for idx,fieldCfg in enumerate(fieldsCfg):
      type = fieldCfg['type']
      name = fieldCfg['name']

      # All this value to ALL the existing records
      # for sqlCfg in allSqlCfg:

      if type=='String':
        sqlFieldValues += "'{moduleName}{name}{indRecord}'".format(**locals())
      elif type=='Integer':
        sqlFieldValues += "22".format(**locals())
      # We generate ONLY 1 record with all the linked tables.
      # @TODO : generate 5^(allFK), so if we have 3 linked tables, that means
      # that for a sinle record we will generate 5^3 : 125 records that has all
      # the combinations
      elif type=='FK':
        totJoins  = totJoins+1
        module    = fieldCfg['config']['FK']['module']
        fieldName = fieldCfg['config']['FK']['fieldName']

        sqlFieldValues += "tbl_{totJoins}.Id".format(**locals())
        sqlFKJoins     += " JOIN {module} tbl_{totJoins} ON tbl_{totJoins}.{fieldName}='{module}{fieldName}1'".format(**locals())

      else:
        raise Exception("Unknown type : {type}".format(**locals()))

      if idx<(totFields-1): sqlFieldValues += ","

    allSqlCfg.append({ 'values' : sqlFieldValues, 'joins' : sqlFKJoins})

  # Build the full SQL sentence
  # See here
  #   http://stackoverflow.com/questions/17661342/mysql-left-join-all-tables
  # to see where
  #   (SELECT 1 FROM DUAL) TMP
  # is used instead
  #   FROM DUAL
  with open(file, 'a') as pFile:
    for sqlCfg in allSqlCfg:
      sqlFieldValues = sqlCfg['values']
      sqlFKJoins     = sqlCfg['joins']

      sql = "INSERT INTO {moduleName} ({sqlFieldNames}) SELECT {sqlFieldValues} FROM (SELECT 1 FROM DUAL) TMP {sqlFKJoins};\n".format(**locals())
      pFile.write(sql)

  print "Generated file {file}!".format(**locals())

# --------------------------------------------------------------- [_genSQLEmpty]
# Generated an empty file the SQL sentences
# ------------------------------------------------------------------------------
def _genSQLEmpty(moduleName, file, printDelete=False):
  if not os.path.exists(file):
    with open(file, 'w') as pFile:
      if printDelete:
        pFile.write("DELETE FROM {moduleName};\n".format(**locals()))

    print "Generated file {file}!".format(**locals())

# ------------------------------------------------------- [_genFullModuleConfig]
# Generate the JSON with the module config
# ------------------------------------------------------------------------------
def _genFullModuleConfig(moduleName, allBasicModulesCfg, sqlOrder, isMinimal, i18nFile):
  fieldsCfg = allBasicModulesCfg[moduleName]['fieldsCfg']
  # NOTE : ok, maybe it's not needed to keep the i18n keys it I am not going
  # to generate the i18nFile, but it's just to void a lot of ifs and this
  # extra effort is nothing for python!!
  i18nKeys={}

  totFields = len(fieldsCfg)
  isIndependentModule = allBasicModulesCfg[moduleName]['moduleCfg']['isIndependentModule'] 

  # ---------------------------------------------------------------------- START
  cfg = "{"

  # --------------------------------------------------------------------- Fields
  cfg += """
  "fields" : ["""

  for idx,fieldCfg in enumerate(fieldsCfg):
    # if field.lower() == "id":
    #   field="__id"
    # elif field.lower() == "idowner":
    #   field="__idOwner"

    type=fieldCfg['type']

    i18nKeys[moduleName + ":" + fieldCfg['name']] = fieldCfg['module'] if type=='FK' else fieldCfg['name']

    # Is a FK
    if type=='FK':
      cfg += """
    {{
      "name" : "{name}",
      "type" : "FK",
      "config" : {{
        "FK" : {{
          "module"  : "{module}",
          "actionName"  : "ListAll",
          "fieldName" : "{fieldName}",
          "relationType" : "{relationType}"
        }}
      }}
    }}""".format(**fieldCfg)
    # Is a String
    elif type=='String':
      cfg += """
    {{
      "name" : "{name}",
      "type" : "String",
      "max_len" : {max_len}
    }}""".format(**fieldCfg)
    # Is a Integer
    elif type=='Integer':
      cfg += """
    {{
      "name" : "{name}",
      "type" : "Integer"
    }}""".format(**fieldCfg)
    # Is a Text
    elif type=='Text':
      cfg += """
    {{
      "name" : "{name}",
      "type" : "Text"
    }}""".format(**fieldCfg)
    # Is a Image
    elif type=='Image':
      cfg += """
    {{
      "name" : "{name}",
      "type" : "Image"
    }}""".format(**fieldCfg)
    # Is a File
    elif type=='File':
      cfg += """
    {{
      "name" : "{name}",
      "type" : "File"
    }}""".format(**fieldCfg)
    # Is a Date
    elif type=='Date':
      cfg += """
    {{
      "name" : "{name}", 
      "type" : "DateTime",
      "format": "dd/MM/yy",
      "time" : "00:00"
    }}""".format(**fieldCfg)
    # Others
    else:
      cfg += """
    {{
      "name" : "{name}",
      "type" : "{type}"
    }}""".format(**fieldCfg)
      # raise Exception ("Unkown data type {type}!".format(**locals()))

    # Add a , (except in the last)
    if idx<(totFields-1): cfg += ","

  cfg += """
  ],"""

  if not isMinimal:
    # ------------------------------------------------------------------- Actions
    cfg += """
  "actions" : ["""

    # Let's build an array with all fields
    allFields = _listFieldsAsString(fieldsCfg)

    # ------------------------------------------------------------------- [Load]
    cfg += """
    {{
      "name" : "Load",
      "type" : "load",
      "params" : [
        {{ "name" : "Id" }}
      ]
    }},""".format(**locals())

    # --------------------------------------------------------------- [ViewFull]
    # (Optional) ViewFull
    # Check if OTHER modules has a FK to THIS ONE.
    # If this is the case, we will create a composed page where we see
    # this item details + a list with all the dependent items
    # @TODO : distinguish the relation of type aggregation and association
    viewFullSections=""
    # When render ViewFull we can pass extra params to show f.ex. in the titles
    extraViewFullParams=""
    for otherModuleName in allBasicModulesCfg:
      for otherFieldsCfg in allBasicModulesCfg[otherModuleName]['fieldsCfg']:
        # OTHER module has a reference to this module
        if otherFieldsCfg['type']=='FK' and otherFieldsCfg['module']==moduleName:
          fieldName=otherFieldsCfg['name']
          relFieldName=otherFieldsCfg['fieldName']
          relType=otherFieldsCfg['relationType']

          if relType=='aggregation':
            # @TODO : now we pass just ONE extra params independent on the number of
            # related items and their needs
            extraViewFullParams=""",
          {{ "name" : "{relFieldName}", "value" : "${relFieldName}" }}
""".format(**locals())

            viewFullSections += """
            ,{{
              "actionName" : "__IGNORE__",
              "module" : "{otherModuleName}",
              "name" : "ListBy{moduleName}",
              "params" : [
                {{ "name" : "{fieldName}" , "value" : "$Id" }}
              ]
            }}""".format(**locals())

    # Ok, we have dependent items, let's create the composed page!!
    if len(viewFullSections)>0:
      cfg += """
    {{
      "name" : "ViewFull",
      "type": "composed",
      "sections" : [
        {{
          "actions" : [
            {{
              "actionName" : "__IGNORE__",
              "module" : "{moduleName}",
              "name" : "ViewAll",
              "params" : [
                {{ "name" : "Id" , "value" : "$Id" }}
              ]
            }}{viewFullSections}
          ]
        }}
      ]
    }},""".format(**locals())

    # Default View Action
    viewAction = "ViewFull" if len(viewFullSections)>0 else "ViewAll"
    extraViewParams = extraViewFullParams if len(viewFullSections)>0 else ""

    # All list for all the Possible FKs
    # That is, this module depends of other modules
    allListFKs=""
    for fieldCfg in fieldsCfg:

      # Only in case of aggregtion has sense to add the AddBy/OmportBy
      if fieldCfg['type']=='FK' and fieldCfg['relationType']=='aggregation':
        module = fieldCfg['module']
        fieldName = fieldCfg['name']
        relFieldName = fieldCfg['fieldName']

        # ------------------------------------------------- [AddBy<OtherModule>]
        # AddBy<Module>
        i18nKeys["{moduleName}:AddBy{module}:Title".format(**locals())]="New {moduleName}".format(**locals())
        i18nKeys["{moduleName}:AddBy{module}:Submit".format(**locals())]="Add".format(**locals())
        i18nKeys["{moduleName}:AddBy{module}:Button".format(**locals())]="Add".format(**locals())

        allFieldsBy=_listFieldsAsString(fieldsCfg, fieldName, True)
        cfg += """
    {{
      "_desc" : "Add a {moduleName} for a certain {module}",
      "name" : "AddBy{module}",
      "type" : "add",
      "fields" : [ {allFieldsBy}
      ],
      "params" : [
        {{ "name" : "{fieldName}" }}
      ]
    }},""".format(**locals())

        # ------------------------------------------------- [ImportBy<OtherModule>]
        # ImportBy<Module>
        i18nKeys["{moduleName}:ImportBy{module}:Title".format(**locals())]="Import {moduleName}".format(**locals())
        i18nKeys["{moduleName}:ImportBy{module}:Submit".format(**locals())]="Import"
        i18nKeys["{moduleName}:ImportBy{module}:Button".format(**locals())]="Import"
        i18nKeys["{moduleName}:ImportBy{module}:OK".format(**locals())]="$totRecords records have been imported successfully"

        allFieldsBy=_listFieldsAsString(fieldsCfg, fieldName, True)
        cfgTransformer = _genTransformer(fieldsCfg, fieldName)
        cfg += """
    {{
      "_desc" : "Import a {moduleName} for a certain {module}",
      "name" : "ImportBy{module}",
      "type" : "import",{cfgTransformer},
      "params" : [
        {{ "name" : "{fieldName}" }}
      ]
    }},""".format(**locals())

        # ------------------------------------------------ [ListBy<OtherModule>]
        # ListBy<Module>
        i18nKeys["{moduleName}:ListBy{module}:Title".format(**locals())]="{moduleName}s".format(**locals())
        i18nKeys["{moduleName}:ListBy{module}:NoData".format(**locals())]="There are no {moduleName}s".format(**locals())

        allFieldsBy=_listFieldsAsString(fieldsCfg, fieldName, False)
        cfg += """
    {{
      "_desc" : "List {moduleName}s for a certain {module}",
      "name" : "ListBy{module}",
      "type" : "list",
      "fields" : [ {allFieldsBy}
      ],
      "onClick" : {{
        "module" : "{moduleName}",
        "actionName" : "{viewAction}",
        "params" : [
          {{ "name" : "Id", "value" : "$Id" }}{extraViewParams}
        ]
      }},
      "globalActions" : [
        {{
          "module" : "{moduleName}",
          "name" : "AddBy{module}",
          "params" : [
            {{ "name" : "{fieldName}", "value" : "${fieldName}" }},
            {{ "name" : "{relFieldName}", "value" : "${relFieldName}" }}
          ]
        }},
        {{
          "module" : "{moduleName}",
          "name" : "ImportBy{module}",
          "params" : [
            {{ "name" : "{fieldName}", "value" : "${fieldName}" }},
            {{ "name" : "{relFieldName}", "value" : "${relFieldName}" }}
          ]
        }}
      ],
      "params" : [
        {{ "name" : "{fieldName}" }}
      ]
    }},""".format(**locals())

    # ----------------------------------------------------------------- [DelAll]
    # DelAll
    # i18nKeys["{moduleName}:DelAll:Title".format(**locals())]="Remove {moduleName}".format(**locals())
    i18nKeys["{moduleName}:DelAll:Button".format(**locals())]="Delete".format(**locals())
    i18nKeys["{moduleName}:DelAll:AskConfirmation".format(**locals())]="Are you sure you want remove this {moduleName}? All related data will be removed too.".format(**locals())
    i18nKeys["{moduleName}:DelAll:Error".format(**locals())]="The {moduleName} could not be removed. Remove first the related data.".format(**locals())
    i18nKeys["{moduleName}:DelAll:OK".format(**locals())]="The {moduleName} has been successfully removed.".format(**locals())

    cfg += """
    {{
      "name" : "DelAll",
      "type" : "del",
      "askConfirmation" : true,
      "beOnly" : true,
      "params" : [
        {{ "name" : "Id" }}
      ]
    }},""".format(**locals())

    # ----------------------------------------------------------------- [ModAll]
    # ModAll
    i18nKeys["{moduleName}:ModAll:Title".format(**locals())]="Edit {moduleName}".format(**locals())
    i18nKeys["{moduleName}:ModAll:Submit".format(**locals())]="Update"
    i18nKeys["{moduleName}:ModAll:Button".format(**locals())]="Edit"

    cfg += """
    {{
      "name" : "ModAll",
      "type" : "mod",
      "fields" : [ {allFields}
      ],
      "params" : [
        {{ "name" : "Id" }}
      ]
    }},""".format(**locals())

    # The dendent modules NOT ha have an Import/Add BUT the ImportBy/AddBy
    if isIndependentModule:
      # --------------------------------------------------------------- [Import]
      # Import
      i18nKeys["{moduleName}:Import:Title".format(**locals())]="Import {moduleName}".format(**locals())
      i18nKeys["{moduleName}:Import:Submit".format(**locals())]="Import"
      i18nKeys["{moduleName}:Import:Button".format(**locals())]="Import"
      i18nKeys["{moduleName}:Import:OK".format(**locals())]="$totRecords records have been imported successfully"

      cfgTransformer = _genTransformer(fieldsCfg)
      cfg += """
    {{
      "name" : "Import",
      "type" : "import",{cfgTransformer}
    }},""".format(**locals())

      # --------------------------------------------------------------- [AddAll]
      # AddAll
      i18nKeys["{moduleName}:AddAll:Title".format(**locals())]="Add {moduleName}".format(**locals())
      i18nKeys["{moduleName}:AddAll:Submit".format(**locals())]="Add"
      i18nKeys["{moduleName}:AddAll:Button".format(**locals())]="Add"

      cfg += """
    {{
      "name" : "AddAll",
      "type" : "add",
      "fields" : [ {allFields}
      ]
    }},""".format(**locals())

    # ----------------------------------------------------------------- [ViewAll]
    # ViewAll : from here we can update or remove an item
    i18nKeys["{moduleName}:ViewAll:Title".format(**locals())]="Details {moduleName}".format(**locals())
    cfg += """
    {{
      "name" : "ViewAll",
      "type" : "view",
      "fields" : [ {allFields}
      ],
      "globalActions" : [
        {{
          "module" : "{moduleName}",
          "name" : "DelAll",
          "params" : [
            {{ "name" : "Id", "value" : "$Id" }}
          ]
        }},
        {{
          "module" : "{moduleName}",
          "name" : "ModAll",
          "params" : [
            {{ "name" : "Id", "value" : "$Id" }}
          ]
        }}
      ],
      "params" : [
        {{ "name" : "Id", "value" : "$Id" }}
      ]
    }},""".format(**locals())

    # ---------------------------------------------------------------- [ListAll]
    # ListAll : from here, we can go add and go to ViewAll / ViewFull
    i18nKeys["{moduleName}:ListAll:Title".format(**locals())]="List {moduleName}s".format(**locals())
    i18nKeys["{moduleName}:ListAll:NoData".format(**locals())]="There are no {moduleName}s".format(**locals())

    cfg += """
    {{
      "name" : "ListAll",
      "type" : "list",
      "fields" : [ {allFields}
      ],
      "onClick" : {{
        "module" : "{moduleName}",
        "actionName" : "{viewAction}",
        "params" : [
          {{ "name" : "Id", "value" : "$Id" }}{extraViewParams}
        ]
      }}""".format(**locals())

    if isIndependentModule:
      cfg += """,
      "globalActions" : [
        {{
          "module" : "{moduleName}",
          "name" : "AddAll"
        }},
        {{
          "module" : "{moduleName}",
          "name" : "Import"
        }}
      ]""".format(**locals())

      
    cfg += """
    }"""

    # Close array actions
    cfg += """
  ],"""

  # -------------------------------------------------------------------- sqlOrder
  cfg += """
  "values" : {{
    "sqlOrder" : {sqlOrder}
  }}""".format(**locals())

  # ------------------------------------------------------------------------ END
  cfg += """
}"""

  if i18nFile:
    with open(i18nFile, 'a') as f:
      f.write("""
# =================================================================
# {moduleName}
# =================================================================""".format(**locals()))
      for key in i18nKeys:
        val=i18nKeys[key]
        f.write("""
{key}={val}""".format(**locals()))

    print "{i18nFile} file updated!".format(**locals())

  return cfg

# ---------------------------------------------------------- [_genUserDashboard]
# Generated the Dashboard for _User
# ------------------------------------------------------------------------------

def _genUserDashboard(allBasicModulesCfg, updAdminPage=False):
  totModules=len(allBasicModulesCfg)

  cfg = """
          {{
            "name" : "MyApp",
            "actions" : [""".format(**locals())

  for idx,moduleName in enumerate(allBasicModulesCfg):
    cfg += """
              {{
                "module" : "{moduleName}",
                "name" : "ListAll"
              }}""".format(**locals())
    if idx<(totModules-1): cfg += ","

  cfg += """
            ]
          }}""".format(**locals())

  if updAdminPage:
    srcFile=os.environ['WEBRAD_HOME'] + '/model/_User.json'
    dstFile=os.environ['PRJ_HOME'] + '/model/_User.json'

    userCfg=json.load(open(srcFile))
    for actionCfg in userCfg['actions']:
      if actionCfg['name']=='HomePageAdmin':
        actionCfg['config']['sections'].insert(0, json.loads(cfg))
    with open(dstFile, 'w') as pFile:
      pFile.write(json.dumps(userCfg))

    print "File {dstFile} updated!".format(**locals())
  else:
    print cfg

# ==============================================================================
# Main
# ==============================================================================
def main(moduleName, allBasicModulesCfg, isMinimal=False, dstFolder=None, sqlOrder=10, generateTestData=None, dstTestData=None, i18nFile=None):
  basicModuleCfg = allBasicModulesCfg[moduleName]

  # -------------------------------------------------------------- Module Config
  # Build the full module config (the JSON)
  jsonFullModuleCfg = _genFullModuleConfig(moduleName, allBasicModulesCfg, sqlOrder, isMinimal, i18nFile)

  # Output the config (stdout or into a file)
  if dstFolder:
    file = "{dstFolder}/{moduleName}.json".format(**locals())
    with open(file, 'w') as pFile:
      pFile.write(jsonFullModuleCfg)
    print "File {file} generated!".format(**locals())
  else:
    print jsonFullModuleCfg

  # ------------------------------------------------------------------- SQL Data
  dstFileTestData=None
  if not dstTestData:
    dstTestData="{PRJ_HOME}/model/custom/ModuleCustom/Database/{DB_TYPE}/{moduleName}".format(**dict(os.environ, **locals()))

  if not os.path.exists(dstTestData):
    os.makedirs(dstTestData)

  dstFileTestData=dstTestData + "/{sqlOrder}-testData" + moduleName + ".sql"

  if generateTestData:
    fullModuleCfg = json.loads(jsonFullModuleCfg)
    _genSQL(moduleName, fullModuleCfg, dstFileTestData)
  else:
    _genSQLEmpty(moduleName, dstFileTestData)

  # CfgData
  dstFileCfgData=dstTestData + "/{sqlOrder}-cfgData" + moduleName + ".sql"
  _genSQLEmpty(moduleName, dstFileCfgData, True)

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  if not 'WEBRAD_HOME' in os.environ:
    raise Exception('Environment variable WEBRAD_HOME not defined!' )

  parser = argparse.ArgumentParser(description='Generates a config file')
  parser.add_argument('fields', nargs='*', help='Field definition in the form Name[:Type]. If Type if not specified, String is used. If Name has de form Id<Module> it is taken as a FK')
  parser.add_argument('--file', help='File with all the modules definitions where every line has de format <ModuleName> : <Field1> ....')
  parser.add_argument('--dst', help='Destination folder where the module definition is genreated (WARNING: file will be overwritten). If --file is used and this parameter is NOT set, $PRJ_HOME/module will be used')
  parser.add_argument('--module', help='The module name.')
  parser.add_argument('--modules', help='If --file is specified, comma separated list of modules')
  parser.add_argument('--minimal', action="store_true", help='Generates minimal configuration')
  parser.add_argument('--generateTestData', action="store_true", help='Generates SQL files to inser the data')
  parser.add_argument('--dstTestData', help='(Optional) Destination folder where the test data SQL will be generaterd. If not especified will be used $PRJ_HOME/model/custom/ModuleCustom/Database/$DB_TYPE/<Module>')
  parser.add_argument('--sqlOrder', default=10000, help='(Optional) Initial SQL order (def=10000, after the core objects). If the core objects have a dependency with the business objects use 10.')
  parser.add_argument('--i18n', action="store_true", help='Generates the i18 file, overwiting if already exists one')
  parser.add_argument('--i18nFile', default=os.environ['PRJ_HOME'] + '/data/i18n/en.properties', help='(Optional) If generates the i18n file, the path to the file (default=' + os.environ['PRJ_HOME'] + '/data/i18n/en.properties')
  parser.add_argument('--updAdminPage', action="store_true", help='If true, updates the file _User.json, the section HomePageAdmin. CAREFUL : this will uglify the json file!!')

  args = parser.parse_args()

  # STEP 1
  # Read a file with ALL the modules definitions and build
  #   allBasicModulesCfg
  # that contains a basic configuration for every module (this is NOT the json)
  allBasicModulesCfg={}
  orderedListModuleName=[]

  # If we have specified to generate the i18n, copy the base from WEBRAD
  if args.i18n:
    if os.environ['WEBRAD_HOME'] + '/data/i18n/en.properties'!=args.i18nFile:
      shutil.copy(os.environ['WEBRAD_HOME'] + '/data/i18n/en.properties', args.i18nFile)

  # Read the config from several modules from a file
  if args.file:
    if not os.path.exists(args.file):
      raise Exception("File {file} does not exist!".format(file=args.file))

    genOnlyThoseModules=None if not args.modules else args.modules.replace(' ','').split(',')
    with open(args.file) as pFile:
      regexCommentLine=re.compile(r" *#.*")
      # [<ModuleName>]
      regexModuleLine=re.compile(r"\[(\w+)\]")

      module=None
      fields=[]

      for _line in pFile:
        line = _line.strip().replace(' ','')
        # line = _line.replace(' ','')
        # Not blank or comment line, then process
        if len(line)>0 and not regexCommentLine.match(line):
          match = regexModuleLine.match(line)
          # Module definition
          if match:
            # This is new module, first generate the precious one
            if len(fields)>0:
              allBasicModulesCfg[module] = _genBasicModuleCfg(module, fields)
              orderedListModuleName.append(module)

            # New module
            module = match.group(1)
            fields=[]
          # Field definition
          else:
            fields.append(line)

      # End of file, generate the last module
      if len(fields)>0:
        if not module:
          raise Exception("Error in configuration, end of file and no module!!")
        allBasicModulesCfg[module] = _genBasicModuleCfg(module, fields)
        orderedListModuleName.append(module)
      else:
        raise Exception("Error in configuration, end of file and no fields!!")
  # Read the info for a single module from the command line
  else:
    allBasicModulesCfg[args.module] = _genBasicModuleCfg(args.module, args.fields)
    orderedListModuleName.append(args.module)

  # STEP 2
  # For every module generate the fullModuleConfig (the JSON) using the
  # basicModuleConfig
  dstFolder=args.dst if args.dst else os.environ['PRJ_HOME'] + '/model'
  sqlOrder=10 if not args.sqlOrder else int(args.sqlOrder)
  for moduleName in orderedListModuleName:
    if not genOnlyThoseModules or moduleName in genOnlyThoseModules:
      main(
        moduleName,
        allBasicModulesCfg,
        args.minimal,
        dstFolder,
        sqlOrder,
        args.generateTestData,
        args.dstTestData,
        args.i18nFile if args.i18n else None
      )
    sqlOrder += 10

  # 3) Generate the JSON files
  _genUserDashboard(allBasicModulesCfg, args.updAdminPage)
