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
import sys
import shutil

# ------------------------------------------------------------------------------
# Generates the documentation
# @param srcDir
# @param dstDir
# @param config
# ------------------------------------------------------------------------------
def generateDoc(srcDir, dstDir, configTemplate):
  if not os.path.exists(srcDir): raise Exception("Source folder {srcDir} does not exist!".format(**locals()))
  if not os.path.exists(configTemplate): raise Exception("Config file {configTemplate} does not exist!".format(**locals()))

  # Rebuild dstDir  
  print "Rebuilding output folder {dstDir} ...".format(**locals())
  if os.path.exists(dstDir): shutil.rmtree(dstDir)
  if not os.path.exists(dstDir): os.makedirs(dstDir)

  # Create the config file
  config=configTemplate + ".tmp"
  shutil.copyfile(configTemplate, config)
  with open(config, "a") as file:
    file.write("""
INPUT             = {srcDir}
EXCLUDE_PATTERNS  = */common/* */log4php/* */logger/* */logs/* */testing/*
OUTPUT_DIRECTORY  = {dstDir}
""".format(**locals()))
  print "Config file {config} generated!".format(**locals())
  
  # Regenerate the documentation
  print "Regenerating the doc for source code in {srcDir}. This can take a while ...".format(**locals())
  utils.system("doxygen " + config)
  
# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generated documentation for PHP')
  parser.add_argument('langs', default=['en'], nargs='*', help='List of langs')
  parser.add_argument('--srcDir', default=os.environ['BE_DST_DIR'], help='Folder where source code is located')
  parser.add_argument('--dstDir', default=os.environ['PRJ_HOME'] + "/docs/phpDoc", help='Folder where the documentation will be generated')
  parser.add_argument('--config', default=os.environ['PRJ_HOME'] + "/scripts/Doxyfile.tmpl", help='File with the Doxygen configuration')

  args = parser.parse_args()

  generateDoc(args.srcDir, args.dstDir, args.config)