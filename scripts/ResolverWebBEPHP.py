#!/usr/bin/python
# -------------------------------------------
# Resolves some variables comning from template
# files and return a value
# -------------------------------------------
import re
from ResolverWeb import ResolverWeb

class ResolverWebBEPHP(ResolverWeb):
  def __init__(self, moduleName, cfgModule, options):
    ResolverWeb.__init__(self, moduleName, cfgModule, options)

  # -------------------------------------------
  # Replacement Methodsr 
  # The function 
  #   printXXX
  # returns the value for the variable
  #   $XXX
  # -------------------------------------------
  
  # $VersionResolver
  def printVersionResolver(self):
    return "1.0" 

  # Module Name
  def printAPP_NAME(self):
    return self.moduleName 