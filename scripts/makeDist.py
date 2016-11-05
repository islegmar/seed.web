#!/usr/bin/python
import os
import argparse
import shutil
import glob
import re
import sys
import zipfile
import tarfile
from MySQLUtils import MySQLUtils
from createWebProject import main as createWebProject
from createWebModule import main as createWebModule

def getAllModulesName():
  moduleNames=[]
  for file in glob.glob(os.environ['PRJ_HOME'] + '/model/*.json'):
    moduleName = re.sub(".json","",os.path.basename(file))
    moduleNames.append(moduleName)

  return moduleNames
   
def generateSqlFile(dstFile, listFiles, mode='w'):
  with open(dstFile, mode) as pDstFile:
    for srcFile in listFiles:  
      with open(srcFile, 'r') as pSrcFile:
        pDstFile.write(pSrcFile.read())

  print "File {dstFile} created!".format(**locals())

# Build a zip file
def addDirToZip(zipHandle, path, basePath=""):
  """
  Adding directory given by \a path to opened zip file \a zipHandle

  @param basePath path that will be removed from \a path when adding to archive

  Examples:
    # add whole "dir" to "test.zip" (when you open "test.zip" you will see only "dir")
    zipHandle = zipfile.ZipFile('test.zip', 'w')
    addDirToZip(zipHandle, 'dir')
    zipHandle.close()

    # add contents of "dir" to "test.zip" (when you open "test.zip" you will see only it's contents)
    zipHandle = zipfile.ZipFile('test.zip', 'w')
    addDirToZip(zipHandle, 'dir', 'dir')
    zipHandle.close()

    # add contents of "dir/subdir" to "test.zip" (when you open "test.zip" you will see only contents of "subdir")
    zipHandle = zipfile.ZipFile('test.zip', 'w')
    addDirToZip(zipHandle, 'dir/subdir', 'dir/subdir')
    zipHandle.close()

    # add whole "dir/subdir" to "test.zip" (when you open "test.zip" you will see only "subdir")
    zipHandle = zipfile.ZipFile('test.zip', 'w')
    addDirToZip(zipHandle, 'dir/subdir', 'dir')
    zipHandle.close()

    # add whole "dir/subdir" with full path to "test.zip" (when you open "test.zip" you will see only "dir" and inside it only "subdir")
    zipHandle = zipfile.ZipFile('test.zip', 'w')
    addDirToZip(zipHandle, 'dir/subdir')
    zipHandle.close()

    # add whole "dir" and "otherDir" (with full path) to "test.zip" (when you open "test.zip" you will see only "dir" and "otherDir")
    zipHandle = zipfile.ZipFile('test.zip', 'w')
    addDirToZip(zipHandle, 'dir')
    addDirToZip(zipHandle, 'otherDir')
    zipHandle.close()
  """
  basePath = basePath.rstrip("\\/") + ""
  basePath = basePath.rstrip("\\/")
  for root, dirs, files in os.walk(path):
    # add dir itself (needed for empty dirs
    # zipHandle.write(os.path.join(root, "."))
    
    # add files
    for file in files:
      filePath = os.path.join(root, file)
      inZipPath = filePath.replace(basePath, "", 1).lstrip("\\/")
      # print filePath + " , " + inZipPath
      # print inZipPath
      zipHandle.write(filePath, inZipPath)

def makeTar(tarFileName,path, basePath=""):
  with tarfile.open(tarFileName, "w") as tar:
    basePath = basePath.rstrip("\\/") + ""
    basePath = basePath.rstrip("\\/")
    for root, dirs, files in os.walk(path):
      # add files
      for file in files:
        filePath = os.path.join(root, file)
        inZipPath = filePath.replace(basePath, "", 1).lstrip("\\/")
        # print filePath + " , " + inZipPath
        # print inZipPath
        tar.add(filePath, inZipPath)

# Make a file with build info
# In Jenkins the environemnt variables:
# BUILD_ID   : The current build id, such as "2005-08-22_23-59-59" (YYYY-MM-DD_hh-mm-ss)
# GIT_COMMIT : SHA of the current commit
def makeFileWithBuildInfo(file):
  with open(file, "w") as pFile:
    buildId = '<Unknown>' if 'BUILD_ID' not in os.environ else os.environ['BUILD_ID']
    gitCommit= '<Unknown>' if 'GIT_COMMIT' not in os.environ else os.environ['GIT_COMMIT']

    pFile.write("""
BUILD_ID   = {buildId}
GIT_COMMIT = {gitCommit}         
""".format(**locals()))

  print "File {file} created!".format(**locals())


# ==============================================================================
# Main
# ==============================================================================
def main(customer=None, distFile=None, distDir=None, verbose=None, createZip=False):
  # ------------------------------------------------------------- Default values
  if not distDir:  distDir  = "{PRJ_HOME}/dist".format(**os.environ)

  # ----------------------------------------------------------- Check the values

  # ---------------------------------------------------------- Generate the code
  if verbose:
    print """
====================================================
customer : {customer}
dist     : {distDir}
====================================================""".format(**locals())

  moduleNames = getAllModulesName()

  # Remove dist folder
  if os.path.exists(distDir):
    if verbose:
      print """
Removing folder {distDir}...""".format(**locals())      
    shutil.rmtree(distDir)

  # Make dist folder
  if not os.path.exists(distDir):
    if verbose:
      print """
Creating folder {distDir}...""".format(**locals())      
    os.makedirs(distDir)
    
  # Create webProject code in dist
  if verbose:
    print """
Generating web code ..."""      
  createWebProject(None,None, {
      'FE' : { 'dst' : distDir + '/fe' },
      'BE' : { 'dst' : distDir + '/be' },
      'Database' : { 'dst' : distDir + '/sql' }
    }, False, verbose)

  # Create modules code in dist
  for moduleName in moduleNames:
    createWebModule(moduleName, None, None, None, {
        'FE' : { 'dst' : distDir + '/fe/' + moduleName },
        'BE' : { 'dst' : distDir + '/be/' + moduleName },
        'Database' : { 'dst' : distDir + '/sql/' + moduleName }
      }, None, verbose, False, False)

  # ---------------------------------------------------------- Generate the sqls
  # TODO : this can be instantiated dynamically based on the kind of database to
  # be used 
  dbUtils = MySQLUtils(distDir + '/sql')  
  
  # ------------------------------------------------------------ Create Database
  # The script to create the database is generated "on the fly" by createDB.py
  # srcFile=os.environ['DB_DST_DIR'] + "/createDatabase.sql"
  # fCreateDB="{distDir}/createDB.sql".format(**locals())
  # shutil.copy(srcFile, fCreateDB)
  
  # ------------------------------------------------ Create Tables & Insert Data
  
  with open("{distDir}/dropTables.sql".format(**locals()), 'w') as pDstFile:
    pDstFile.write("SET foreign_key_checks = 0;\n")

  generateSqlFile(
    "{distDir}/dropTables.sql".format(**locals()), 
    dbUtils.dropModuleTable(moduleNames,False),
    'a'
  )

  with open("{distDir}/dropTables.sql".format(**locals()), 'a') as pDstFile:
    pDstFile.write("SET foreign_key_checks = 1;\n")

  generateSqlFile(
    "{distDir}/createTables.sql".format(**locals()), 
    dbUtils.createModuleTable(moduleNames,False)
  )
      
  generateSqlFile(
    "{distDir}/permissions.sql".format(**locals()), 
    dbUtils.recreateModulePermissions(moduleNames,False)
  )

  generateSqlFile(
    "{distDir}/insertCfgData.sql".format(**locals()), 
    dbUtils.insertModuleCfgData(moduleNames,False)
  )

  generateSqlFile(
    "{distDir}/i18n.sql".format(**locals()), 
    dbUtils.recreateI18N(False)
  )

  generateSqlFile(
    "{distDir}/insertTestData.sql".format(**locals()), 
    dbUtils.insertModuleTestData(moduleNames,False)
  )

  generateSqlFile(
    "{distDir}/allModules.sql".format(**locals()), 
    dbUtils.updateTblModule(moduleNames,False)
  )

  # ------------------------------------------------------------- Copy Utilities
  shutil.copy("{PRJ_HOME}/scripts/dist/installApp.{FE_TYPE}_{BE_TYPE}.py".format(**os.environ), distDir + "/installApp.py")
  shutil.copy("{PRJ_HOME}/scripts/dist/createDB{DB_TYPE}.py".format(**os.environ), distDir + "/createDB.py")
  shutil.copy("{PRJ_HOME}/scripts/dist/utils.py".format(**os.environ), distDir + "/utils.py")
  print "Script files copied!"

  # --------------------------------------------------------- Copy Documentation
  shutil.copy("{PRJ_HOME}/README.md".format(**os.environ), distDir)
  shutil.copytree("{PRJ_HOME}/docs".format(**os.environ), distDir + "/docs")
  print "Documentation copied!"

  # --------------------------------------------------------------- Config Files
  srcFile="{PRJ_HOME}/scripts/dist/env.json".format(**os.environ)
  dstFile="{distDir}/env.json".format(**locals())
  
  with open(dstFile, 'w') as pDstFile:
    with open(srcFile, 'r') as pSrcFile:
      pDstFile.write(pSrcFile.read().format(**os.environ))

  print "Generated config file {dstFile}!".format(**locals())

  # ---------------------------------------------- Create a file with build info
  makeFileWithBuildInfo(distDir + '/fe/version.txt')

  # ------------------------------------------------------------- Make dist file 
  print "Generated distribution file ... "

  # Create a zip file
  if createZip:
    if not distFile: distFile = "{PRJ_HOME}/{PRJ_NAME}.zip".format(**os.environ) 

    zipf = zipfile.ZipFile(distFile, 'w')
    addDirToZip(zipf, distDir, distDir)
    zipf.close()
  # (Default) Create a tar
  else:
    if not distFile: distFile = "{PRJ_HOME}/{PRJ_NAME}.tar".format(**os.environ) 

    makeTar(distFile,distDir, distDir)

  print "Generated distribution file {distFile}!".format(**locals())

  # -------------------------------------------------------------- Apagayvamonos

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generates the dist for the app')
  parser.add_argument('--customer', help='The customer id, if we want to build multitenance')
  parser.add_argument('--dist', help='The dist folder')
  parser.add_argument('--file', help='The zip file')
  parser.add_argument('--zip', action="store_true", help='Create a zip instead a tar')
  parser.add_argument('-v', '--verbose', action="store_true", help='Verbose')

  args = parser.parse_args()

  main(args.customer, args.file, args.dist, args.verbose, args.zip)