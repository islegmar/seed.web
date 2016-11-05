#!/usr/bin/python
# ------------------------------------------------------------------------------
# Common utilities used by the Web/Module generators
# ------------------------------------------------------------------------------
import os
import glob
import tempfile
import utils
import codecs

class MySQLUtils:
  def __init__(self, dbDstDir=None):
    # Base dir where the scripts are located
    self.dbDstDir = dbDstDir if dbDstDir else os.environ['DB_DST_DIR']

  # Find a serie of files based on fiel patterns returned by fFilePattern and run 
  # them in a certain order (if needed) 
  def _runListFiles(self, modules, fFilePattern, order=False, runSql=True):
    # Because we use glob (we don't have the file, just a pattern), that
    # will return an array that wit the loop module will build a matrix that we 
    # have to convert back to a 1D array
    #files = [f  for module in modules for f in glob.glob(func(module)) if os.path.exists(f)]
    files = [f for module in modules for f in glob.glob(self.dbDstDir + "/" + module + "/" + fFilePattern(module)) if os.path.exists(f)]

    # Order the list if needed
    theList = files if not order else sorted(files, key = lambda x: int(os.path.basename(x).split("-")[0]))

    # Execute the list of files
    if runSql:
      for file in theList:
        #print "Run {local} ({file})".format(local=os.path.basename(file), file=file)
        print "{local}".format(local=os.path.basename(file), file=file)
        self.run_sql_file(file)
      
    return theList

  # ============================================================================
  # Public Functions
  # ============================================================================
  def run_sql_file(self,fSql, pUsr=None, pPwd=None, pDb=None, pHost=None, pPort=None):
    usr   = pUsr  if pUsr  is not None else os.environ['MYSQL_USR']
    pwd   = pPwd  if pPwd  is not None else os.environ['MYSQL_PWD']
    db    = pDb   if pDb   is not None else os.environ['MYSQL_DB']
    host  = pHost if pHost is not None else os.environ['MYSQL_SERVER']
    port  = pPort if pPort is not None else os.environ['MYSQL_PORT']

    #print "Run {fSql} as {usr}@{db} on {host}".format(**locals())
      
    mysql_exe=os.environ['MYSQL_EXE']
    cmd="{mysql_exe} --user={usr} --password={pwd} --host={host} --port={port} {db} < {fSql}".format(**locals())
    utils.system(cmd)   

  def run_sql_cmd(self,sql, pUsr=None, pPwd=None, pDb=None, pHost=None, pPort=None):
    # Create a Temporary file with the sql
    fTemp = tempfile.NamedTemporaryFile(delete=False)                        
    fTempName=fTemp.name                                                                 
    try:   
      fTemp.write(sql)
      fTemp.close()
      self.run_sql_file(fTempName, pUsr, pPwd, pDb, pHost, pPort)
    finally:                                                                
      # Automatically cleans up the file                                  
      os.unlink(fTempName)   

  # ---------------------------------------------------------- Create the MySQL DB
  def createDatabase(self):
    file=self.dbDstDir + "/createDatabase.sql" 
    #print "Created database {MYSQL_DB} on {MYSQL_SERVER}. Added user {MYSQL_USR}".format(**locals())
    print "Created database".format(**locals())
    self.run_sql_file(
      self.dbDstDir + "/createDatabase.sql", 
      os.environ['MYSQLROOT_USR'], 
      os.environ['MYSQLROOT_PWD'],
      ''
    )

  def updateTblModule(self,moduleNames,runSql=True):
    return self._runListFiles(
      moduleNames, 
      lambda module : "insert{module}Into_Module.sql".format(module=module),
      False,
      runSql
    )


  def dropModuleTable(self,moduleNames,runSql=True):
    return self._runListFiles(
      moduleNames, 
      lambda module : "*drop{module}.sql".format(module=module),
      True,
      runSql
    )

  def createModuleTable(self,moduleNames,runSql=True):
    return self._runListFiles(
      moduleNames, 
      lambda module : "*create{module}.sql".format(module=module),
      True,
      runSql
    )

  def insertModuleCfgData(self,moduleNames,runSql=True):
    return self._runListFiles(
      moduleNames, 
      lambda module : "*cfgData{module}.sql".format(module=module),
      True,
      runSql
    )

  def insertModuleTestData(self,moduleNames,runSql=True):
    return self._runListFiles(
      moduleNames, 
      lambda module : "*testData{module}.sql".format(module=module),
      True,
      runSql
    )

  def recreateModulePermissions(self,moduleNames,runSql=True):
    return self._runListFiles(
      moduleNames, 
      lambda module : "*permission{module}.sql".format(module=module),
      True,
      runSql
    )

  # Build the SQL for _Lang and _I18N and run (if neded it)
  def recreateI18N(self,runSql=True):
    if runSql:
      print "Regenerating the tables _Lang and _I18N, this can take a while ..."
    # See ResolverWebrad.py to know why this is taken directly from 
    # environment variables and not passed as argument
    srcDir = os.environ['PRJ_I18N_DIR']
    langs  = os.environ['PRJ_LANGS'].split(",")

    # Check all the exepcted files exist
    for lang in langs:
      file="{srcDir}/{lang}.properties".format(**locals())
      if not os.path.exists(file):
        raise Exception ("File {file} does not exist!".format(**locals()))


    # Generate _Lang      
    fileLang=self.dbDstDir + "/_Lang.sql"
    with codecs.open(fileLang, 'w', encoding="utf-8") as fDst: 
      fDst.write("""
DELETE FROM _Lang;""")
      for lang in langs:
        fDst.write("""
INSERT INTO _Lang (Locale, Orientation) VALUES ( '{lang}', 'LTR' );""".format(**locals()))

    # print "Created {file}!".format(**locals())   

    if runSql:
      self.run_sql_file(fileLang)

    # Generate _I18N
    fileI18N=self.dbDstDir + "/_I18N.sql"
    with codecs.open(fileI18N, 'w', encoding="utf-8") as fDst: 
      fDst.write("""
DELETE FROM _I18N;""")
      for lang in langs:
        # Load all the translations
        trans=utils.file2Dict("{srcDir}/{lang}.properties".format(**locals()))
        
        for key in sorted(trans):
          value=trans[key]
          # NOW REMOVED
          # Insert ONLY if we do not have it in the DB. This protect to update a 
          # value we have changes from the web
          if False:
            fDst.write(u"""
INSERT INTO _I18N (Name, Text, Id_Lang) 
  SELECT '{key}','{value}', Id FROM _Lang 
   WHERE Locale='{lang}' AND NOT EXISTS 
    (SELECT * FROM _I18N WHERE Name='{key}' AND Id = _Lang.Id);""".format(**locals()))
          else:
            fDst.write(u"""
INSERT INTO _I18N (Name, Text, Id_Lang) 
  SELECT '{key}','{value}', Id FROM _Lang 
   WHERE Locale='{lang}';""".format(**locals()))
            
    print "Created {fileI18N}!".format(**locals())

    if runSql:
      self.run_sql_file(fileI18N)
    
    return [fileLang, fileI18N]