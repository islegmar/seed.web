# ------------------------------------------------------------------------------
# Script that creates the MySQL database
# ------------------------------------------------------------------------------
import os
import glob
import argparse
import tempfile
import json
import utils

# ============================================================================
# Functions
# ============================================================================

# Executes an SQL file
def _runSqlFile(fSql, usr, pwd, db, host=None, port=None):
  host      = utils.getValue(host, 'MYSQL_SERVER')
  port      = utils.getValue(port, 'MYSQL_PORT', 3306)
  mysql_exe = utils.getValue(None, 'MYSQL_EXE', 'mysql')

  cmd="{mysql_exe} --user={usr} --password={pwd} --host={host} --port={port} {db} < {fSql}".format(**locals())
  os.system(cmd)   

def _runSqlCmd(sql, pUsr=None, pPwd=None, pDb=None, pHost=None, pPort=None):
    # Create a Temporary file with the sql
    fTemp = tempfile.NamedTemporaryFile(delete=False)                        
    fTempName=fTemp.name                                                                 
    try:   
      fTemp.write(sql)
      fTemp.close()
      _runSqlFile(fTempName, pUsr, pPwd, pDb, pHost, pPort)
    finally:                                                                
      # Automatically cleans up the file                                  
      os.unlink(fTempName)   

# ==============================================================================
# Main
# ==============================================================================
def main(createDB=False, skipTestData=False, skipI18N=False, mysqlRootUsr=None, mysqlRootPwd=None, mysqlUsr=None, mysqlPwd=None, mysqlDb=None, mysqlHost=None, mysqlPort=None):
  
  # Load config
  config=json.load(open("env.json"))

  # Get the values for db/usr/pwd
  mysqlDb  = utils.getValue(mysqlDb , 'MYSQL_DB' )
  mysqlUsr = utils.getValue(mysqlUsr, 'MYSQL_USR', mysqlDb)
  mysqlPwd = utils.getValue(mysqlPwd, 'MYSQL_PWD', mysqlDb)

  # ------------------------------------------------------------ Create Database
  if createDB:
    createDBSql="""
DROP DATABASE IF EXISTS {mysqlDb};
CREATE DATABASE IF NOT EXISTS {mysqlDb};
GRANT ALL PRIVILEGES ON {mysqlDb}.* TO {mysqlUsr}@localhost IDENTIFIED BY '{mysqlPwd}';  
""".format(**locals())  

    # Get the usr/pwd for root, so we can create the database
    mysqlRootUsr = utils.getValue(mysqlRootUsr, 'MYSQLROOT_USR')
    mysqlRootPwd = utils.getValue(mysqlRootPwd, 'MYSQLROOT_PWD')

    print "Creating the database {mysqlDb} ...".format(**locals())
    _runSqlCmd(createDBSql, mysqlRootUsr, mysqlRootPwd, 'mysql', mysqlHost, mysqlPort)
    print "Database created!"

  # ---------------------------------------------------------------- Drop Tables
  print "Dropping tables into the database {mysqlDb} ...".format(**locals())
  _runSqlFile("dropTables.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
  print "Tables removed!"

  # -------------------------------------------------------------- Create Tables
  print "Creating tables into the database {mysqlDb} ...".format(**locals())
  _runSqlFile("createTables.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
  print "Tables created!"

  # ---------------------------------------------------------- Create Permission
  print "Inserting permissions into the database {mysqlDb} ...".format(**locals())
  _runSqlFile("permissions.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
  print "Permissions inserted!"

  # Insert Config Data
  print "Inserting config data into the database {mysqlDb} ...".format(**locals())
  _runSqlFile("insertCfgData.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
  print "Config data inserted!"

  # ---------------------------------------------------------------- Insert I18N
  if skipI18N:
    print "*** Skip insert I18N data"
  else:
    print "Inserting I18N data into the database {mysqlDb}. This can take a while ...".format(**locals())
    _runSqlFile("i18n.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
    print "I18N data inserted!"

  # ----------------------------------------------------------- Insert Test Data
  if skipTestData:
    print "*** Skip insert test data"
  else:
    print "Inserting test data into the database {mysqlDb} ...".format(**locals())
    _runSqlFile("insertTestData.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
    print "Test data inserted!"

  # --------------------------------------------------------- All Modules Config
  print "Inserting all modules config into the database {mysqlDb} ...".format(**locals())
  _runSqlFile("allModules.sql", mysqlUsr, mysqlPwd, mysqlDb, mysqlHost, mysqlPort)
  print "Module config data inserted!"

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generates the MySQL database')
  parser.add_argument('--rootUsr', help='Database user (root)')
  parser.add_argument('--rootPwd', help='Database password (root)')
  parser.add_argument('--usr', help='Database user')
  parser.add_argument('--pwd', help='Database password')
  parser.add_argument('--db', help='Database name')  
  parser.add_argument('--host', help='Database host')
  parser.add_argument('--port', help='Database port')
  parser.add_argument('--createDB', action="store_true", help='Create the database')
  parser.add_argument('--skipTestData', action="store_true", help='Do not insert the test data')
  parser.add_argument('--skipI18N', action="store_true", help='Do not insert the I18N data')


  args = parser.parse_args()

  main(
    args.createDB,
    args.skipTestData,
    args.skipI18N,
    args.rootUsr,
    args.rootPwd,
    args.usr,
    args.pwd,
    args.db,
    args.host,
    args.port
  )