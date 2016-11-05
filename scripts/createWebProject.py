#!/usr/bin/python
# ------------------------------------------------------------------------------
# This script generates the basis for a web application (code, files,...) using
# several templates. 
# The web is divided in two partes:
# * Front End (FE)
# * Back End (FE)
# In theory, several technologies/solutions can be used and mixed (fex. FE in 
# pure HTML and a BE in PHPor Java). In any case, a different template will be 
# used
#
# @TODO : In this script also the DB is created but now only MySQL is supported but
# other databases could be supported without too much effort.
# ------------------------------------------------------------------------------
import os
import shutil
import tempfile
import re
import json
import argparse
import sys
import importlib
from MySQLUtils import MySQLUtils
import utils
# import createPHPModule

# ==============================================================================
# Main
# ==============================================================================

def main(prjName=None,templatesDir=None,components={},createDB=False, verbose=False):  
  # Check the environment has been set properly
  if not 'PRJ_NAME' in os.environ:
    raise Exception("Environment not set. Please execute '. setenv.sh' first!")

  # Default values  
  if not prjName: prjName = os.environ['PRJ_NAME']
  if not templatesDir: templatesDir = os.environ['PRJ_TEMPLATES_DIR'].split(",")
  
  if 'FE'   not in components:       components['FE'] = {}
  if 'type' not in components['FE']: components['FE']['type'] = os.environ['FE_TYPE']
  if 'dst'  not in components['FE']: components['FE']['dst']  = os.environ['FE_DST_DIR']

  if 'BE'   not in components:       components['BE'] = {}
  if 'type' not in components['BE']: components['BE']['type'] = os.environ['BE_TYPE']
  if 'dst'  not in components['BE']: components['BE']['dst']  = os.environ['BE_DST_DIR']

  if 'Database' not in components:             components['Database'] = {}
  if 'type'     not in components['Database']: components['Database']['type'] = os.environ['DB_TYPE']
  if 'dst'      not in components['Database']: components['Database']['dst']  = os.environ['DB_DST_DIR']

  # TODO : this can be instantiated dynamically based on the kind of database to
  # be used
  dbUtils = MySQLUtils()  

  python=os.environ['PYTHON_EXE']

  if verbose:
    print """
---------------------------------------------------
[Web Project]
+ prjName     : {prjName}
+ templates   : {templates}""".format(**dict(templates=json.dumps(templatesDir),**locals()))
  
  for compoName in components:
    if verbose:
      print """
[{compoName}]
+ Type     : {type}
+ Dst dir  : {dst}""".format(**dict(compoName=compoName,**components[compoName]))

  if verbose:
    print """
+ createDB      : {createDB}
+ MYSQL_SERVER  : {MYSQL_SERVER}
+ MYSQL_PORT    : {MYSQL_PORT}
+ MYSQLROOT_USR : {MYSQLROOT_USR}
+ MYSQLROOT_PWD : {MYSQLROOT_PWD}
+ MYSQL_DB      : {MYSQL_DB}
+ MYSQL_USR     : {MYSQL_USR}
+ MYSQL_PWD     : {MYSQL_PWD}
---------------------------------------------------""".format(**dict(locals(),**os.environ))

  # ------------------------------------------- Process the different components
  for compoName in components:
    type=components[compoName]['type']
    dst=components[compoName]['dst']

    if not os.path.exists(dst):
      print 'Destination folder {dst} does not exist, create it.'.format(**locals())
      os.makedirs(dst)

    # --- Generate code using template
    # @TODO : change genModule.py so we can call it as a python module
    for dir in templatesDir:
      template="{dir}/Web/{compoName}/{type}".format(**locals())
      if os.path.exists(template): 
        if verbose:
          print """
---------------------------------------------------
[{compoName} : Web Project]
{template}
---------------------------------------------------""".format(**locals())
        cmd="{python} genModule.py -r ResolverWeb{compoName}{type} -t {template} -d {dst} {prjName}".format(**locals())
        utils.system(cmd)
  
    # --- Add custom code if any  
    for dir in templatesDir:
      custom="{dir}/WebCustom/{compoName}/{type}".format(**locals())
      if os.path.exists(custom): 
        if verbose:
          print """
---------------------------------------------------
[{compoName} : Custom Web Project]
{custom}
---------------------------------------------------""".format(**locals())
        cmd="{python} genModule.py -r ResolverWeb{compoName}{type} -t {custom} -d {dst} {prjName}".format(**locals())
        utils.system(cmd)

  # ----------------------------------------------------- Other Optional Actions
  if createDB:
    dbUtils.createDatabase()

# ==============================================================================
# Command line arguments
# ==============================================================================
if __name__ == "__main__":
  # Check the environment has been set properly
  if not 'PRJ_NAME' in os.environ:
    raise Exception("Environment not set. Please execute '. setenv.sh' first!")

  parser = argparse.ArgumentParser(description='Generates an web app (FE and BE) using several technologies')
  parser.add_argument('name', nargs='?', help='The name of the generate Web')
  parser.add_argument('--fe', help='Technology used for the FE (PHP, HTML)')
  parser.add_argument('--feDst', help='Destination folder for the generated code for the FE')
  parser.add_argument('--be', help='Technology used for the BE (PHP, Java)')
  parser.add_argument('--beDst', help='Destination folder for the generated code for the BE')
  parser.add_argument('--db', help='Technology used for the Database (MySQL, Oracle)')
  parser.add_argument('--dbDst', help='Destination folder for the generated sql files are created')
  parser.add_argument('--createDB', action="store_true", help='Create the database');
  parser.add_argument('--templates', help='Folder where the templates are located. Several locations separated by ,')
  parser.add_argument('--verbose',action="store_true", help='Print verbose messages')

  args = parser.parse_args()

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

  # Call main
  main(
    args.name,
    None if not args.templates else args.templates.split(','),
    components,
    args.createDB,
    args.verbose
  )