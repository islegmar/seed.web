#!/usr/bin/python
# -------------------------------------------
# Substitute variables in a collection of template 
# files by a serie of values using a resolver  
# -------------------------------------------
import re
import json
import argparse
import os
import sys
import importlib

# -------------------------------------------
# Output the cfg file as HTML
# If firstKeys is not None, if is a ordered list
# with the fist attributes will be shown when printing
# every field value
# -------------------------------------------
def printCfgAsHtml(moduleName, cfg, firstKeys):
  # Create a list with all the keys in the right order
  orderedKeys = firstKeys[:] if firstKeys else []
  for key in cfg['fields'][0].keys():
    if key not in firstKeys:
      orderedKeys.append(key)

  print """
<!doctype html>
<head>
  <meta charset="utf-8">
</head>
<body>
  <h1>%s</h1>
  <h2>Fields</h2>
  <table border="1">
""" % moduleName

  # Attributes
  print "<thead><tr>"
  for key in orderedKeys:
    print "<th>%s</th>" % key
  print "</tr></thead>"

  # Values for every field
  print "<tbody>"
  for field in cfg['fields']:
    print "<tr>"
    for key in orderedKeys:
      if key not in field:
        print "<td>Undefined</td>"
      else:
        print "<td>%s</td>" % field[key]
    print "</tr>"
  print "</tbody>"

  print """
  </table>
"""
  # Values
  print """
  <h2>Values</h2>
"""

  if 'values' not in cfg:
    print "<p>No values defined</p>"
  else:
    print "<table border='1'>"
    for key in cfg['values'].keys():
      print "<tr><td><b>%s</b></td><td>%s</td>" % (key, cfg['values'][key])
    print "</table>"

  print """
</body>
</html>
"""

# -------------------------------------------
# MAIN
# -------------------------------------------
# --- Read arguments
parser = argparse.ArgumentParser(description='Generates a module using template.')
parser.add_argument('name', help='The name of the generate module')
parser.add_argument('-t','--template', help='The folder containing the template be used', default="module")
parser.add_argument('-d','--destination', help='The folder where the module will be generated', default="./out")
parser.add_argument('-r','--resolver', help='Resolver to be used', default="Resolver")
parser.add_argument('-c','--cfg', help='File with the config file. If not specified, the file ./[moduleName].json')
parser.add_argument('-k','--keys', help='Comma separated with the attribute names ordered when printing as html');
parser.add_argument('-i','--info', action='store_true', help='Print a html with the ingo in the config file')
parser.add_argument('-v','--values', help='Values overwritten the config')
parser.add_argument('--minimal',action="store_true", help='Do not generate default actions as ListAll, ....')
parser.add_argument('--dirTmpls', help='List of of folders where templates are locates')
parser.add_argument('--dirModelFiles', help='Folders where the JSON files with the models are located')


args = parser.parse_args()
 
# --- Get arguments
moduleName=args.name
moduleNameLower=moduleName[:1].lower() + moduleName[1:]
templateDir=args.template
baseDstDir=args.destination
resolverName=args.resolver
# Load dictionary with the medatada
if args.cfg:
  # Cfg can be a file with the metadata or a string with it
  if os.path.exists(args.cfg):
    cfgModule=json.load(open(args.cfg))
  else:
    print args.cfg 
    cfgModule=json.loads(args.cfg)
else:
  if os.path.exists(moduleName + ".json"):
    cfgModule=json.load(open(moduleName + ".json"))
  else:
    cfgModule={}

# If we have defined values in the command line, update the ones retrieved from
# the config file 
if args.values:
  if not 'values' in cfgModule:
    cfgModule['values'] = {}

  for keyVal in args.values.split(","):
    tmp = keyVal.split('=')
    key = tmp[0].strip()
    val = tmp[1].strip()
    cfgModule['values'][key] = val

# --- Check arguments
# Folder with the template does not exit (only check if not print)
if not args.info and not os.path.exists(templateDir):
  sys.exit("Folder " + templateDir + " with the template does not exists!")

if args.info:
  printCfgAsHtml(moduleName, cfgModule, args.keys.replace(" ","").split(',') if args.keys else [])
else:
  # Instantiate the resolver dynamically
  # from Resolver import Resolver
  # resolver = Resolver(moduleName, cfgModule)
  # This is equivalent to:
  #   from module import resolverName
  module = importlib.import_module(resolverName)
  cResolver = getattr(module, resolverName)
  resolver = cResolver(moduleName, cfgModule, args)
  # @TODO : ERROR, it's tool late!!! The init tries to use some of the properties 
  # that are set here. There are two options: 
  # - Add all those options in the creator => Not like, because adding a new option 
  #   means change ALL the creators
  # - Change the calls:
  #   + creator()
  #   + set()
  #   + init()
  # - Add an argument options : {}  in the creator
  # resolver.setMinimal(args.minimal)
  resolver.resolveDir(templateDir, baseDstDir)
  # Add a post action, after the baseDir have been processed
  resolver.shutdown()


# @TODO : Ideally, we should have ALWAYS in any Python script something like 
# this at the end:
#
#   def main(arg1, arg2, etc):
#      # do whatever the script does
#   if __name__ == "__main__":
#      main(sys.argv[1], sys.argv[2], sys.argv[3])
#
# That means se can call it from command line or as a module from another script
