#!/usr/bin/python
# -------------------------------------------
# Resolves some variables comning from template
# files and return a value
# -------------------------------------------
import os
import re
from ResolverWeb import ResolverWeb

class ResolverWebDatabaseMySQL(ResolverWeb):
  def __init__(self, moduleName, cfgModule, options):
    ResolverWeb.__init__(self, moduleName, cfgModule, options)

  # -------------------------------------------
  # Replacement Methodsr 
  # -------------------------------------------
  
  # $VersionResolver
  def printVersionResolver(self):
    return "V1.0" 

  def printMYSQL_DB(self):
    return os.environ['MYSQL_DB']

  def printMYSQL_SERVER(self):
    return os.environ['MYSQL_SERVER']

  def printMYSQL_USR(self):
    return os.environ['MYSQL_USR']

  def printMYSQL_PWD(self):
    return os.environ['MYSQL_PWD']