#!/usr/bin/python
import os
import shutil
import utils
import re
import genI18N

# -------------------------------------------
# Base Resolver for the webrad project
# -------------------------------------------
from Resolver import Resolver

class ResolverWebrad(Resolver):
  def __init__(self, moduleName, cfgModule, options):
    Resolver.__init__(self, moduleName, cfgModule, options)

    # The only thing common to all the components (Web, Module), ALMOST all artifacts 
    # (FE, BE but not Database) and providers (SOOCSS, PHP) is the I18N
    # (Mental Note : Probably tomorrow that will no be true :-))

    # NOTE : Thos variables are not specified as argument but taken from 
    # the environment variables just to make the things easier. If not we have to:
    # - Change all the calls that genreate web/module
    # - Change MySQLUtils that needs those values to generate the SQL   
    if not 'PRJ_I18N_DIR' in os.environ:
      raise Exception("Please, review your setenv file, environment variable PRJ_I18N_DIR not defined!!") 
    if not 'PRJ_LANGS' in os.environ:
      raise Exception("Please, review your setenv file, environment variables PRJ_LANGS not defined!!") 

    # Array with all the I18N keys
    self.i18nKeys = []
    
    # Path with the global files with all the translations are located
    self.dirI18NFiles = os.environ['PRJ_I18N_DIR']
    # Langs
    self.langs = os.environ['PRJ_LANGS'].split(",")

    # ---------------------------------------- Provide some default translations
    # Short day names
    self.i18n("DayMinMo")
    self.i18n("DayMinTu")
    self.i18n("DayMinWd")
    self.i18n("DayMinTh")
    self.i18n("DayMinFr")
    self.i18n("DayMinSa")
    self.i18n("DayMinSu")

    # Months
    self.i18n("Month01")
    self.i18n("Month02")
    self.i18n("Month03")
    self.i18n("Month04")
    self.i18n("Month05")
    self.i18n("Month06")
    self.i18n("Month07")
    self.i18n("Month08")
    self.i18n("Month09")
    self.i18n("Month10")
    self.i18n("Month11")
    self.i18n("Month12")

    # Generic Errors
    self.i18n("UploadFile:MimeTypeNotAllowed")
    self.i18n("UploadFile:FileSizeNotAllowed")

  # ------------------------------------------------------------------- Resolver
  # After processing the files, we have in self.i18nKeys a serie of keys that 
  # msut be added in the translations file
  # @TODO : maybe this process could be optimized because the ENTIRE FILE is
  # generated EVERY TIME. That means, if we generate 10 modules, the entire 
  # file is regenerated, adding the new keys. It is OK like it is, becasuse the
  # process is fast, but is goot to know that just in case in the future it is
  # not fast :-) 
  def shutdown(self):
    if self.i18nKeys:
      for lang in self.langs:
        globalI18NFile=self.dirI18NFiles + "/" + lang + ".properties"

        # Build a dictionary with all the existing translations
        globalDict={}
        if os.path.exists(globalI18NFile):  
          globalDict = utils.file2Dict(globalI18NFile)

        # Add ONLY the keys we have found
        for key in self.i18nKeys:
          if key not in globalDict:
            globalDict[key]=key

        # Regenerate the global file, now with the new keys    
        genI18N.genI18NFile(globalDict, globalI18NFile)

  # ----------------------------------------------------------- Common Functions
  # Add a new key for the translations
  def _addI18NKey(self, key):
    #newKey = self.moduleName + ":" + key
    if not key in self.i18nKeys:  
      self.i18nKeys.append(key)

    return key

  # ----------------------------------------------------- Substitution Functions
  # @TODO : Not sure if we should have this kind of functions here, but is a way
  # to have centralized all the I18N stuff (more or less ...)
  # By detault, add this to the list and return the value. 
  # This can be overwritten in FE and BE if the desired output is something else 
  def i18n(self, vars):
    return self._addI18NKey(vars) 