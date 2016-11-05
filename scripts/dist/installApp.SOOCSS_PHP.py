# ------------------------------------------------------------------------------
# Script that install the app
# ------------------------------------------------------------------------------
import argparse
import os
import utils
import json
import shutil

# ==============================================================================
# Functions
# ==============================================================================
def _copyDir(src, dst):
  if not os.path.exists(src):
    raise Exception("Source folder {src} does not exist!".format(**locals()))

  # Renove the destination folder 
  if os.path.exists(dst):
    shutil.rmtree(dst)

  # Copy the files
  shutil.copytree(src, dst)

  print "Copied files into {dst}!".format(**locals())

# ==============================================================================
# Main
# ==============================================================================
def main(dstDir):
  
  # Load config
  # config=json.load(open("env.json"))
  # prjName=config['prjName']

  # Install FE and BE
  _copyDir('fe', "{dstDir}/fe".format(**locals()))
  _copyDir('be', "{dstDir}/be".format(**locals()))

  # Copy documentation
  shutil.copy("README.md","{dstDir}".format(**locals()))
  _copyDir('docs', "{dstDir}/docs".format(**locals()))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Install the app')
  parser.add_argument('dstFolder', help='The folder where htdocs is located (fex. /var/www/html). The folders [prj]/fe and [prj]/be will be created under this folder.')

  args = parser.parse_args()

  main(args.dstFolder)