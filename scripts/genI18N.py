#!/usr/bin/python
# ==============================================================================
# Utilities relates with the I18N files
# NOTE : We have used the previous existing file genI18N.py but it has redone
#
# We're using the python utility to translate
# https://github.com/terryyin/google-translate-python 
# ==============================================================================

import os
import argparse
import utils
import re
import shutil
import codecs

# ------------------------------------------------------------------------------
# Generates a file with the translations, nicely grouped
# NOTE : because we're working with unicode, we can not build composed strings
# like
#   "{key}={value}".format(**locals())
# ------------------------------------------------------------------------------
def genI18NFile(globalDict, dstFile):
  # print len(globalDict)
  
  # Reorganize the info in:
  # - Global keys
  # - Module keys
  #   - General
  #   - Actions
  # We use [] because we want to keep the order
  reKeyWithModule = re.compile("^(\w+):\w+$")     
  reKeyWithModuleAction = re.compile("^(\w+):(\w+):\w+$")     

  globalKeys={}
  moduleKeys={}

  for key in globalDict:
    value=globalDict[key]
    moduleName=None
    actionName=None

    match=reKeyWithModuleAction.match(key)
    # Module+Action 
    if match:
      moduleName=match.group(1)
      actionName=match.group(2)
    else:  
      match=reKeyWithModule.match(key)
      # Module (no Action)
      if match:
        moduleName=match.group(1)

    if moduleName:
      # Create the elements if not exists
      if moduleName not in moduleKeys:
        moduleKeys[moduleName] = {
          'globals' : {},
          'actions' : {}
        }     
        
      if actionName and actionName not in moduleKeys[moduleName]['actions']:
        moduleKeys[moduleName]['actions'][actionName] = {}

      # Save the value
      if actionName:
        moduleKeys[moduleName]['actions'][actionName][key] = value
      else:
        moduleKeys[moduleName]['globals'][key] = value
    else:
      globalKeys[key] = value

  # Regenerate the global file, now with the new keys    
  # Create a backup file
  if os.path.exists(dstFile):  
    shutil.copyfile(dstFile,dstFile+".backup")
  
  # Regenerate the file, removing the previous content 
  tot2=0
  with codecs.open(dstFile, "w", encoding="utf-8") as fFile:
    # allKeys = sorted(globalDict)

    # -------------------------------------------------------------- Global Keys
    fFile.write("""
# -----------------------------------------------
# Global keys
# -----------------------------------------------""")

    for key in sorted(globalKeys):
      fFile.write("\n" + key + "=")
      fFile.write(globalKeys[key])
      tot2=tot2+1

    # -------------------------------------------------------------- Module Keys
    for moduleName in sorted(moduleKeys):
      fFile.write("""

# -----------------------------------------------
# {moduleName}
# -----------------------------------------------""".format(**locals()))

      # Globals
      fFile.write("""

# Globals""")
  
      for key in sorted(moduleKeys[moduleName]['globals']):
        fFile.write("\n" + key + "=")
        fFile.write(moduleKeys[moduleName]['globals'][key])
        tot2=tot2+1

      # By Action
      for actionName in sorted(moduleKeys[moduleName]['actions']):
        fFile.write("""

# Action : {actionName}""".format(**locals()))
  
        for key in sorted(moduleKeys[moduleName]['actions'][actionName]):
          fFile.write("\n" + key + "=")
          fFile.write(moduleKeys[moduleName]['actions'][actionName][key])
          tot2=tot2+1

  # print tot2
  # print "{dstFile} generated!".format(**locals())

# ------------------------------------------------------------------------------
# Rebuild the I18N files, regenereting the full project   
# ------------------------------------------------------------------------------
def regenerateI18NFiles():
  baseDir=os.environ['PRJ_I18N_DIR']
  langs=os.environ['PRJ_LANGS'].split(",")

  # Create security copies for every file and remove it, so it is full regenerated 
  print "Backing up the I18N files ..."
  setOldI18N={}
  for lang in langs:
    file="{baseDir}/{lang}.properties".format(**locals())
    if os.path.exists(file):
      setOldI18N[lang]=utils.file2Dict(file)
      shutil.copyfile(file,file+".backup")
      os.remove(file)

  # Regenerate the project, so the I18N files are regenerated
  # @TODO : NOT call the command line
  print "Regenereting the I18N files ..."
  python=os.environ['PYTHON_EXE']
  utils.system(python + " createWebProject.py")
  utils.system(python + " createWebModule.py --all")

  # Adding in the generated files the translations we already had
  for lang in langs:
    file="{baseDir}/{lang}.properties".format(**locals())
    print "Recreating the file {file} ...".format(**locals())
    
    newI18N=utils.file2Dict(file)
    oldI18N=[] if not lang in setOldI18N else setOldI18N[lang]

    # Add values coming from the old file
    for key in newI18N:
      if key in oldI18N:
        newI18N[key]=oldI18N[key]
        del oldI18N[key]

    # Regenerate the file
    genI18NFile(newI18N, file)

    # Print unused keys
    print """
----------------------------------
[Unused keys for lang '{lang}']""".format(**locals())
    
    for key in oldI18N:
      print key
    
    print """
----------------------------------"""

# ------------------------------------------------------------------------------
# Translate the texts is 'srcFile' and generate so many files as 'langs'  
# ------------------------------------------------------------------------------
def translate(baseLang, srcFile, langs, dstDir):
  from translate import Translator

  if not os.path.exists(srcFile):
    raise Exception("File {srcFile} does not exist!".format(**locals()))
  
  srcDict = utils.file2Dict(srcFile)

  for lang in langs:
    dstFile = "{dstDir}/{lang}.properties".format(**locals())
    dstDict = {} if not os.path.exists(dstFile) else utils.file2Dict(dstFile)
    translator= Translator(from_lang=baseLang,to_lang=lang)

    print "Translating {baseLang} => {lang} ({dstFile}) ...".format(**locals())
    for key in srcDict:
      # Already translated
      if key not in dstDict or dstDict[key]==key:
        srcStr=srcDict[key]
        print "'{srcStr}' ...".format(**locals())
        dstStr=translator.translate(srcStr)
        #print "'{srcStr}' => '{dstStr}'".format(**locals())
        dstDict[key] = dstStr
    print "Translation done!"

    genI18NFile(dstDict, dstFile)

# ------------------------------------------------------------------------------
# Set a default translation for a key that follows a regular expression
# ------------------------------------------------------------------------------
def setDefaultTranslation4Key(langs, baseSrcDir, matchKey, value):
  for lang in langs:
    srcFile = "{baseSrcDir}/{lang}.properties".format(**locals())
    srcDict = {} if not os.path.exists(srcFile) else utils.file2Dict(srcFile)

    tot=0
    for key in srcDict:
      # Not translated
      if key==srcDict[key] and matchKey in key:
          tot += 1
          srcDict[key]=value

    print "{tot} keys have been updated!".format(**locals())
          
    genI18NFile(srcDict, srcFile)

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Utilities for the I18N files')
  parser.add_argument('langs', default=['en'], nargs='*', help='List of langs')
  parser.add_argument('--baseLang', default='en', help='Base lang for the translations')
  parser.add_argument('--dstDir', default=os.environ['PRJ_I18N_DIR'], help='Base dir where the I18N files are located')
  parser.add_argument('--translate', help='Comma separated of langs to translate')
  parser.add_argument('--regenerate', action="store_true", help='Regenerate the I18N files')
  parser.add_argument('--key', help='Regular expression to identify a key, in case we want to translate a bunch of them')
  parser.add_argument('--value', help='Value used to translate the key (if nor previous translation exist)')

  args = parser.parse_args()

  if args.regenerate:
    regenerateI18NFiles()

  if args.translate:
    translate(
      'en',
      args.dstDir + "/" + args.baseLang + ".properties",
      args.translate.split(","),
      args.dstDir
    )  

  if args.key:
    if args.value:
      setDefaultTranslation4Key(
        args.langs,
        args.dstDir,
        args.key,
        args.value
      )  
    else:
      raise Exception("--key provided but NOT --value")  

  # Default values, taken from the environment
  
  #main(i18nFile, srcDirs.split(','), sqlFile)
