#!/usr/bin/python
# ------------------------------------------------------------------------------
# This script complements 'createWebProject.py' and generates a module for a web 
# application (code, files,...) usinseveral templates. 
# The module is divided in two partes:
# * Front End (FE)
# * Back End (FE)
# In theory, several technologies/solutions can be used and mixed (fex. FE in 
# pure HTML and a BE in PHPor Java). In any case, a different template will be 
# used
# ------------------------------------------------------------------------------

import os
import sys
import glob
import re
import shutil
import tempfile
import json
import utils
import argparse
from MySQLUtils import MySQLUtils
import ResolverModule

# ==============================================================================
# Main
# ==============================================================================
# - templatesDir : array of folder where we can find templates
def main(moduleName, appName=None, cfgFile=None, templatesDir=None, components=None, additionalConfigValues=None,verbose=False,nogen=False, genDefaultActions=False,dirModelFiles=None):
  # Check the environment has been set properly
  if not 'PRJ_NAME' in os.environ:
    raise Exception("Environment not set. Please execute '. setenv.sh' first!")

  # Default values  
  if not appName: appName = os.environ['PRJ_NAME']
  if not cfgFile:  cfgFile = os.environ['PRJ_HOME'] + "/model/{moduleName}.json".format(**locals())
  if not templatesDir: templatesDir = os.environ['PRJ_TEMPLATES_DIR'].split(",")
  if not dirModelFiles: dirModelFiles = os.environ['PRJ_HOME'] + '/model'

  if 'FE'   not in components:       components['FE'] = {}
  if 'type' not in components['FE']: components['FE']['type'] = os.environ['FE_TYPE']
  if 'dst'  not in components['FE']: components['FE']['dst']  = os.environ['FE_DST_DIR'] + "/" + moduleName

  if 'BE'   not in components:       components['BE'] = {}
  if 'type' not in components['BE']: components['BE']['type'] = os.environ['BE_TYPE']
  if 'dst'  not in components['BE']: components['BE']['dst']  = os.environ['BE_DST_DIR'] + "/" + moduleName

  if 'Database'   not in components:       components['Database'] = {}
  if 'type' not in components['Database']: components['Database']['type'] = os.environ['DB_TYPE']
  if 'dst'  not in components['Database']: components['Database']['dst']  = os.environ['DB_DST_DIR'] + "/" + moduleName


  # TODO : this can be instantiated dynamically based on the kind of database to
  # be used
  dbUtils = MySQLUtils()  
   
  python=os.environ['PYTHON_EXE']
    
  if verbose:
    print """---------------------------------------------------
[Web Module]
+ appName                  : {appName}  
+ moduleName               : {moduleName}
+ cfgFile                  : {cfgFile}
+ templates                : {templates}
+ additionalConfigValues   : {additionalConfigValues}
+ genDefaultActions        : {genDefaultActions}
+ dirModelFiles            : {dirModelFiles}
""".format(**dict(templates=json.dumps(templatesDir),**locals()))
    for compoName in components:
      print """
[{compoName}]
+ {type} : {dst}
""".format(**dict(compoName=compoName,**components[compoName]))
    print "---------------------------------------------------"
  else:
    if not nogen:
      print """
[{appName} : {moduleName}]""".format(**locals())
      # Use verbose!!
      # for compoName in components:
      #  print "+ {compoName} ({type}) : {dst}".format(**dict(compoName=compoName,**components[compoName]))
  
  # Generate the code
  if not nogen:
    if not cfgFile:
      cfgFile=moduleName + '.json'

    # @TODO : review. The additional config values, should be globals or by
    # compo type
    compoAdditionalConfigValues="prjName={appName}".format(**locals())
    if additionalConfigValues:
      additionalConfigValues += "," + compoAdditionalConfigValues
    else:  
      additionalConfigValues = compoAdditionalConfigValues

    # Aditional generation options 
    optDefaultActions = "--genDefaultActions" if genDefaultActions else ""
    optDirModelFiles = "--dirModelFiles " + dirModelFiles if dirModelFiles else "" 

    # ------------------------------------------- Process the different Components
    for compoName in components:
      type=components[compoName]['type']
      dst=components[compoName]['dst']

      if not os.path.exists(dst):
        os.makedirs(dst)
      
      # IL - 26/04/15 - Provide JSON config to the custom files  
      # See note in ResolverModule.py about need to have this variable
      dirTmpls=""
      for dir in templatesDir:
        template="{dir}/Module/{compoName}/{type}".format(**locals())
        if os.path.exists(template): 
          if verbose:
            print """
---------------------------------------------------
[{compoName} : Module Template]
{template}
---------------------------------------------------""".format(**locals())
          # Use verbose!
          # else:
          #  print "{compoName} template: {template}".format(**locals())
          
          if len(dirTmpls)>0: dirTmpls += ","
          dirTmpls += template

          cmd="{python} genModule.py -r ResolverModule{compoName}{type} -c {cfgFile} -t {template} -d {dst} -v {additionalConfigValues} {optDefaultActions} {optDirModelFiles} {moduleName}".format(**locals())
          utils.system(cmd)

      # --- Add custom code (if exists) for THIS specific module
      for dir in templatesDir:
        custom="{dir}/ModuleCustom/{compoName}/{type}/{moduleName}".format(**locals())
        if os.path.exists(custom): 
          if verbose:
            print"""
---------------------------------------------------
[{compoName} : Custom Module Template]
{custom}
---------------------------------------------------""".format(**locals())
          # Use vebose!
          # else:
          #   print "FE custom : {custom}".format(**locals())

          cmd="{python} genModule.py -r ResolverModule{compoName}{type} -c {cfgFile} -t {custom} -d {dst} -v {additionalConfigValues} --dirTmpls {dirTmpls} {optDefaultActions} {optDirModelFiles} {moduleName}".format(**locals())
          utils.system(cmd)
 
    # ------------------------------------------------- Add all the translations
    # Add to the global I18N file all the keys found while processing this 
    # module that are kept in i18nKeys

if __name__ == "__main__":
  # Check the environment has been set properly
  if not 'PRJ_NAME' in os.environ:
    raise Exception("Environment not set. Please execute '. setenv.sh' first!")

  parser = argparse.ArgumentParser(description='Generates an web app using the PHP templates')
  parser.add_argument('moduleName', nargs='?', help='The name of the generated module')
  parser.add_argument('--prj', help='The name of the app')
  parser.add_argument('--fe', help='Technology used for the FE (PHP, SOOCSS)')
  parser.add_argument('--feDst', help='Destination folder for the generated code for the FE')
  parser.add_argument('--be', help='Technology used for the BE (PHP, Java)')
  parser.add_argument('--beDst', help='Destination folder for the generated code for the BE')
  parser.add_argument('--db', help='Technology used for the Database (MySQL, Oracle)')
  parser.add_argument('--dbDst', help='Destination folder for the generated sql files are created')
  parser.add_argument('--fileCfg', help='File with the configuration')
  parser.add_argument('--templates', help='List of folders where the templates can be found')
  parser.add_argument('--all',action="store_true", help='Generate the code for all modules')
  parser.add_argument('--values', help='Values overwritten the config')
  parser.add_argument('--verbose',action="store_true", help='Print verbose messages')
  parser.add_argument('--nogen',action="store_true", help='No generate the code')
  parser.add_argument('--defaultActions',action="store_true", help='Generate default actions as ListAll, ....')
  
  # Database's actions
  parser.add_argument('--recreatePermissions',action="store_true", help='Regenerate the _Permission table')
  parser.add_argument('--createModuleTable',action="store_true", help='Create the database tables')
  parser.add_argument('--insertTestData',action="store_true", help='Insert test data')
  parser.add_argument('--updateTblModule',action="store_true", help="Update _Module table this module's config")
  parser.add_argument('--recreateI18N',action="store_true", help="Regenerate tables _Lang and _I18N")

  parser.add_argument('--full',action="store_true", help='The same that recreatePermissions, createModuleTable, insertTestData, updateTblModule and recreateI18N')
  
  #parser.add_argument('--sqlFile', help='File with testing SQL data for that module')

  args = parser.parse_args()

  # List of module names we are going to generate
  moduleNames = None                                                          
  if args.all or args.full:                                                   
    moduleNames=[]                                                            
    for file in glob.glob(os.environ['PRJ_HOME'] + '/model/*.json'):          
      moduleName = re.sub(".json","",os.path.basename(file))                  
      moduleNames.append(moduleName)                                          
    moduleNames=sorted(moduleNames)                                           
  else:                                                                       
    moduleNames = [args.moduleName]                                           

  # Loop over all the module names
  for moduleName in moduleNames: 
    # Default values
    components = {}  
    if args.fe and args.feDst:
      components['FE'] = {
        'type' : args.fe,
        'dst' : args.feDst
      }
    if args.be and args.beDst:
      components['BE'] = {
        'type' : args.be,
        'dst' : args.beDst
      }
    if args.db and args.dbDst:
      components['Database'] = {
        'type' : args.db,
        'dst' : args.dbDst
      }

    main(
      moduleName, 
      args.prj,
      args.fileCfg, 
      None if not args.templates else args.templates.split(','),
      components,
      args.values,
      args.verbose,
      args.nogen,
      args.defaultActions,
      os.environ['PRJ_HOME'] + '/model'
    )

  # TODO : this can be instantiated dynamically based on the kind of database to
  # be used
  dbUtils = MySQLUtils()  
  
  # Create the tables
  if args.full or args.createModuleTable:
    dbUtils.dropModuleTable(moduleNames)
    dbUtils.createModuleTable(moduleNames)

  # We have to insert the test data AFTER all the tables have been created
  if args.full or args.recreatePermissions:
    dbUtils.recreateModulePermissions(moduleNames)

  # Insert config data
  if args.full or args.createModuleTable:
    dbUtils.insertModuleCfgData(moduleNames)

  # We have to insert the test data AFTER all the tables have been created AND
  # also the permissions (for _User)
  if args.full or args.insertTestData:
    dbUtils.insertModuleTestData(moduleNames)

  # Update module table
  if args.full or args.updateTblModule:
    dbUtils.updateTblModule(moduleNames) 

  # Regenerate the I18N
  dbUtils.recreateI18N(args.full or args.recreateI18N)   