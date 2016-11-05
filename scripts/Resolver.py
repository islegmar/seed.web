#!/usr/bin/python
# -------------------------------------------
# Resolves some variables comning from template
# files and return a value
# -------------------------------------------
import re
import os
import json
import shutil
import traceback

class Resolver:
  # This a SHARED MUTABLE variable shared among all the instances, so we can
  # get unique ids (and not random). This is used actually in the FE to generate 
  # unqiue IDs for the Widgets ( see {NewWidgetID} and {CurrentWidgetID})
  SHARED_COUNTER = 1
  
  def __init__(self, moduleName, cfgModule, options):  
    self.moduleName = moduleName
    self.moduleNameLower=self.moduleName[:1].lower() + self.moduleName[1:]
    self.cfgModule = cfgModule
    self.options = options

    self.genDefaultActions = False #self.options.minimal
    
    # Capture things like {funcName(arg}}]
    self.regexFullFunc=re.compile(r"{\w+\([^()]*\)}") 
    # If data = regexFuncArgs.findall('{funcName(argument)}'), then
    # data[0][0] = funcName
    # data[0][1] = argument
    self.regexFuncArgs=re.compile(r"{(\w+)\((.*)\)}") 
    self.regexCommentLine=re.compile(r" *##")
    self.regexStartIf=re.compile(r" *@@if *([^ *]*)")
    self.regexElse=re.compile(r" *@@else")
    self.regexEndIf=re.compile(r" *@@endif")

    self.regexVariable=re.compile(r"{\w+}")
    
    # Utility : DISABLED : the cfgModule is updated in the resolvers, if we keep
    # here a reference, it will be out of date!!!!
    # self.allFields = None if not 'fields' in cfgModule else cfgModule['fields']
    
    # Actual processing paths
    self.templateDir = None
    self.baseDstDir = None
    # Current processing files
    self.currSrcFile=None
    self.currDstFile=None


  # ============================================================================
  # Public Functions
  # ============================================================================

  # Copy the file structure from 'templateDir' into 'baseDstDir', resolving
  # the variables inside the files and the file names.
  def resolveDir(self, templateDir, baseDstDir):
    self.templateDir = templateDir
    self.baseDstDir = baseDstDir

    # Create the destination folder (intermediate also)
    if not os.path.exists(baseDstDir):
      os.makedirs(baseDstDir)

    # Find templates and generate them
    # Also generate all the directory structure
    transformFiles=True
    for (path, dirs, files) in os.walk(templateDir):        
      # IL - 19/03/15 - If the file ".webrad-notransform" exists in a folder, the
      # files are copied but NOT transformed
      if os.path.exists(os.path.join(path,".webrad-notransform")):
        transformFiles=False
      elif os.path.exists(os.path.join(path,".webrad-transform")):
        transformFiles=True  

      # Folders in this entry : create them in the destination folder
      for dir in dirs:
        srcDir=os.path.join(path,dir)
        dstDir=self.getDstPath(srcDir)
        if not os.path.exists(dstDir):
          os.mkdir(dstDir)
  
      # print ">>> path : {path}, transformFiles : {transformFiles}".format(**locals())

      # Files in this entry : they are templates that need to be copied
      # in the destination folder once transformed
      for file in files:
        srcFile=os.path.join(path,file)
        dstFile=self.getDstPath(srcFile)
        # The current status is transform the files
        if transformFiles:
          try:
            self.genFileFromTmpl(srcFile, dstFile)
          except Exception, e:
            errorMsg = str(e)
            print """
=========================================================
ERROR while processing file 

srcFile : {srcFile}
dstFile : {dstFile}
msg     : {errorMsg}

=========================================================
""".format(**locals())
            raise
        # The current status is just copy the files
        else:
          shutil.copy(srcFile, dstFile)

  # Useful method called when the folders have been proceessed. Typically this 
  # will be overwritten by the Resolvers
  def shutdown(self):
    pass

  # ============================================================================
  # Protected/Private Functions
  # ============================================================================
  # Resolve all the vars in a string
  def resolveAllVars(self, content):
    buff=content

    # --- Functions : they have the form fex.:
    # {funcName(argument)}
    # List of all the variables with arguments
    listOfFullFuncWithVars = set(self.regexFullFunc.findall(buff))
    for fullFuncWithVars in listOfFullFuncWithVars:
      data = self.regexFuncArgs.findall(fullFuncWithVars)
      funcName = data[0][0]
      # If there are several arguments comman separated, vars will contains all 
      # the vars resolved, comma separaated
      vars = self.resolveAllVars(data[0][1]).replace(" ", "")
      # Execute this function with its arguments and resolve all the ocurrences
      # with the result of that execution
      funcArgs = vars.split(",")
      buff = buff.replace(fullFuncWithVars, getattr(self, funcName)(*funcArgs))
    
    # --- Normal variables
    # List of variables for that line
    listOfVars = set(self.regexVariable.findall(buff))
    # Transform, changing all the variables 
    for varName in listOfVars:
      buff = buff.replace(varName, self.resolveVar(varName))

    return buff

  # Resolve a single variable, calling the related function
  # The variable identified as:
  #   {VarName}
  # is resolved:
  # - If defined in the dictionary 'values'
  # - Calling the function 'print{VarName}()'
  def resolveVar(self, var):
    # Get the varName removing the delimites
    varName = var.replace('{','').replace('}','')

    # Is the variable in the dictionary?
    if 'values' in self.cfgModule and varName in self.cfgModule['values']:
      return str(self.cfgModule['values'][varName])
    # Otherwise, call the printXXX() method
    else:
      fName = 'print' + varName
      # TODO : A nice way to check if the function exists!!
      return getattr(self, fName)()
      try:
        pass
      except AttributeError:
        print "WARNING : Function '{fName}' does not exist in '{resolver}' while processing '{currSrcFile}'!".format(fName=fName, resolver=self.__class__.__name__,currSrcFile=self.currSrcFile)
        return var
      except:
        print "ERROR evaluating function '{fName}' using resolver '{resolver}' while processing file '{currSrcFile}'!".format(fName=fName, resolver=self.__class__.__name__,currSrcFile=self.currSrcFile)
        raise
        
  # Returns the name of the expected destination file (or folder) giving the sorce one
  def getDstPath(self, srcPath, resolveVars = True):
    dstPath=os.path.join(self.baseDstDir, re.sub(r'^' + self.templateDir, '.', srcPath))

    # Resolve the paths dstPath can contain
    return self.resolveAllVars(dstPath) if resolveVars else dstPath

  # Generate 'dstFile' using the template 'tmplFile' and 
  # resolving the variables with the class 'resolver'
  # The variables are identified as:
  #   {VarName}
  def genFileFromTmpl(self, tmplFile, dstFile=None, itemCfg=None):
    if itemCfg: self.currentItemCfg=itemCfg
    
    # This file is included in another using the function
    # {include(...)}
    # IL - 20/03/15 - Do nothing, just pass. If needed, this need to be specified
    # in the config json or as additional config (see fex. startHTML)
    if os.path.basename(tmplFile).endswith(".inc"):
      pass
    else:
      self.currSrcFile=tmplFile
      self.currDstFile=dstFile

      # Output is a file
      if dstFile:
        with open(dstFile, 'w') as fDstFile: 
          fDstFile.write(self._processFile(tmplFile))
      # Return the output as string
      else:
        return self._processFile(tmplFile)

  # Process a file and return a String with the contents
  def _processFile(self, tmplFile):
    buff=""

    outputLine=True
    insideIfBlock=False
    numLine=0
    with open(tmplFile) as fTmpl:
      for line in fTmpl.readlines():
        ++numLine

        # @TODO : refractor the code, use elif istead those nested blocks
        
        # --- Comment lines
        if self.regexCommentLine.match(line):
          continue
        # --- End if
        if self.regexEndIf.match(line):
          if not insideIfBlock:
            raise Exception("Found en @@endif without an @@if while processing {tmplFile} at line number {numLine}".format(**locals()))
          outputLine=True
          insideIfBlock=False
        else:
          # --- Start If
          match=self.regexStartIf.match(line)
          if match:
            testExpr=self.resolveAllVars(match.group(1)).strip()
            # @TODO : make it better; nos we just evaluate the expression and 
            # if it returns ANYTING, it is considered a True (even if it 
            # returns something like false)
            outputLine=len(testExpr)>0
            insideIfBlock=True
          else:
            # --- Else
            if self.regexElse.match(line):
              if not insideIfBlock:
                raise Exception("Found en @@else without an @@if while processing {tmplFile} at line number {numLine}".format(**locals()))
            
              # Ok, we have to 'reverse' the value of outputLine:
              # + If it is True, that means the if tests was ok and we have
              #   to ignore the else block
              # + If it is False, that means the if tests was NOT ok and we have
              #   to process the else block
              outputLine=not outputLine
            # --- Regular line (no comment, no if/else/endif/....)  
            else:  
              if outputLine:
                # Write in dst the transformed line
                # DO NOT USE directly + to concat strings (problems with unicode)
                # @TODO : sure there is a more "pythonic" way of doing the things! ;-)
                buff = "{buff}{newLine}".format(buff=buff, newLine=self.resolveAllVars(line))
    
    return buff

        

  # ============================================================================
  # 
  # Replacement Methods resolving functions like
  # 
  # {func(args)} ----> @TODO : at the moment only one argument allowed
  #
  # ============================================================================

  def include(self,fileName):
    if fileName:
      if os.path.exists(fileName):
        # return self.resolveAllVars(''.join(open(fileName).readlines()))
        return self._processFile(fileName)
      else:
        raise Exception("File {fileName} does not exist!".format(**locals()))  
    else:
      return ""

  # As first step to make a more generic code, use this function to retrieve
  # the "environment" variables, so in the future we can specify those
  # variables in config files (that was the first idea) instead of believing
  # in the environment. We're not going to migrate all the code, but start using
  # this function isntead os.environ[]
  def Environ(self, varName):
    if varName in self.options: return self.options[varName] 
    if varName in os.environ: return os.environ[varName]

    raise Exception("The variable {varName} is not defined in 'options' neither 'os.environ'") 
  
  def urlBE(self,vars):
    raise Exception("The function urlBE() class MUST be overwritten with the RELATIVE paths");
    # return self.Environ('BE_CONTEXT') + '/be' + vars
    
  def urlFE(self, vars):
    raise Exception("The function urlFE() class MUST be overwritten with the RELATIVE paths");
    # return self.Environ('FE_CONTEXT') + '/fe' + vars     
    
  def urlSoocss(self, vars):
    return self.urlFE('/include/external/soocss' + vars)     

  def urlInternal(self, vars):
    return self.urlFE('/include/internal' + vars)     
    
  def urlExternal(self, vars):
    return self.urlFE('/include/external' + vars)     

  # ============================================================================
  # 
  # Generic Replacement Methods 
  #
  # ============================================================================

  # $VersionResolver
  def printVersionResolver(self):
    return "V1.0" 
