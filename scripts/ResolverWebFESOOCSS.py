#!/usr/bin/python
# -------------------------------------------
# Resolves some variables comning from template
# files and return a value
# -------------------------------------------
import re
import os
from ResolverWeb import ResolverWeb

class ResolverWebFESOOCSS(ResolverWeb):
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

  def printAPP_NAME(self):
    return self.moduleName

  def printprjName(self):
    return self.moduleName

  def printstartHTML(self):
    return os.environ['START_HTML_FILE']

  def printendHTML(self):
    return os.environ['END_HTML_FILE']    

  # @TODO : we need this method here because the place where this variable is
  # needed (_end.ind) it is used by Modules and by Generic pages. In case a non
  # module page, return "" so nothing is added  
  def printBreadcrumbTitle(self):
    return ""    

  # Return the value for body/@id (<body id="{PageID}">)
  # @TODO : return a value based on the file name?
  def printPageID(self):
    return ""  

  # Return the value for body/@class (<body class="{PageClassname}">)
  def printPageClassname(self):
    return ""  

  # These functions are called by FE pages that are in [appContext]/fe, like
  # can be index.html or login.html
  def urlBE(self,vars):
    return '../be' + vars
    
  def urlFE(self, vars):
    return '.' + vars  