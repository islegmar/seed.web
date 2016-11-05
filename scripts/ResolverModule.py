#!/usr/bin/python
# -------------------------------------------
# Base Resolver for the Web part
# -------------------------------------------
import re
import os
import sys
import json
import utils
import glob
from ResolverWebrad import ResolverWebrad
#from ResolverModuleBEPHP import ResolverModuleBEPHP
#from ResolverModuleFESOOCSS import ResolverModuleFESOOCSS


class ResolverModule(ResolverWebrad):
  def __init__(self, moduleName, cfgModule, options):
    # print "[" + moduleName + "] " + self.__class__.__name__ + "()"
    ResolverWebrad.__init__(self, moduleName, cfgModule, options)

    if 'transformer' in cfgModule:
      raise Exception('Old configuration in {moduleName}. Now "transformer" MUST go inside de import actions'.format(**locals()))

    # There are some files that are in fact templates (well, metatemplates in 
    # fact! :-)) that will generate a bunch of files. For example if in the cfg
    # we have defined several 'mod forms' (one of them with their fields that 
    # can be accessed, security constraints,...), evey of those forms and all
    # the related files will be generated using some templates. For example
    # for one 'mod form', the following files are involved:
    # - /views/_{ActionName}{MODULE}.mod.php : generated code
    # - /views/{ActionName}{MODULE}.mod.php : custom code that included the generated code
    # - /service/_{ActionName}{MODULE}.mod.php : generated code that perrform bean
    #                                        validations and update in DB
    # - /service/{ActionName}{MODULE}.mod.php : custom code that includes the generated code
    # So, if we are in the module 'Voter' and have a form 'Review1', following 
    # files will be generated
    # - /views/_modReview1Voter.php 
    # - /views/modReview1Voter.php 
    # - /service/_Mod{Review1Voter.php 
    # - /service/ModReview1Voter.php
    #
    # The template files have the form:
    # <fileName>.<action>.tmpl
    self.listTemplates = {
    }
    # Pattern
    self.tmplFilesPattern = re.compile("^(.*)\.(\w+)\.tmpl$")     

    # Special case for the templates : using one template we can generate several 
    # and this variable points to the configuration we're using at this moment
    self.currentItemCfg = None

    # When generating the current module we need to know also the config for ALL
    # the modules, so we can e.g. configure views from other modules, permissions,....
    # @TODO it can be overkill to compute that for EVERY Resolver instead no it
    # once or pass it as parameter. If we do it that ways is because in THEORY we
    # could mix different Resolver and MYBE some of them overwrite the normalize
    self.allModulesConfig={}
    allConfigFiles = glob.glob(options.dirModelFiles + '/*.json')
    for file in allConfigFiles:          
      otherName=re.sub(".json","",os.path.basename(file))
      cfgModule=json.load(open(file))
      self.normalizeCfg(otherName, cfgModule, False)

      # @TODO : chapuza :-( add some missing values
      if not 'values' in cfgModule: cfgModule['values'] = {}
      if not 'prjName' in  cfgModule['values']: cfgModule['values']['prjName'] = self.cfgModule['values']['prjName']
      self.allModulesConfig[otherName]=cfgModule

      # Dump this in a file
      with open(options.dirModelFiles + "/" + otherName + ".json.full", "w") as pFile:
        pFile.write(json.dumps(self.allModulesConfig[otherName]))

    # Normalize the module's configuration
    # We extract it the already normalized modules
    self.cfgModule = self.allModulesConfig[self.moduleName]

    # Config used to generate any destination file
    self.filesConfig = self._buildFilesConfig()


  # ============================================================================
  # ProtectedMethods
  # ============================================================================
  
  def setCurrentItemCfg(self, cfg):
    self.currentItemCfg = cfg

  # Complete field's info
  # In 'fields' we have the full info about fields: name, type, config,....
  # Some of those fields are used in other places (fex. the list of fields to
  # be shown in a list) and in those other fields we only have the field name,
  # we do not have the full field info but we need it (a typical case is the 
  # type). This method completes the info
  def completeFieldInfo(self,listFieldsWithLittleInfo, listFieldsWithFullInfo):
    for fieldCfg in listFieldsWithLittleInfo:
      # For that fields, get the full field configuration 
      fullFieldCfg = utils.search_dictionaries('name', fieldCfg['name'], listFieldsWithFullInfo)   

      # If we refer to a field that has not been declared before (in the 
      # 'fields') section this is a TEMPORAL field
      # (see the document NOT_PERSISTENT_FIELD.md for +info) 
      # IL - 17/06/15 - transient is an attribute NOT a data type
      if not fullFieldCfg:
        fullFieldCfg = {}
        # @TODO : refractor, so the property transient could be removed
        fullFieldCfg['transient'] = True
        # IL - 03/07/15  
        fullFieldCfg['temporal'] = True
        fullFieldCfg['readOnly'] = False        
        fullFieldCfg['hide'] = False        
        fullFieldCfg['type'] = 'String'
        fullFieldCfg['max_len'] = 255
        
      # Copy the missing keys
      # @TODO : can be done in one line mixing dictionaries
      for k in fullFieldCfg:       
        if not k in fieldCfg:  
          fieldCfg[k] = fullFieldCfg[k] 

  # --------------------------------------------------------------------------
  # Normalize, put some default values, reorganize some values so it is easier
  # to access to them....
  # --------------------------------------------------------------------------
  # @TODO : review, so if we are resolving for all the modules with do not 
  # exectue this EACH time (e.g. now, if we have 10 modules we normalize each
  # module 10 times)
  def normalizeCfg(self,moduleName, cfgModule, genDefaultActions=False):

    # ------------------------------------------------ Reorganize Fields' config
    # Reorganize some info so it is easier to access to it. That is, the specific
    # configuration for a certain kind of field type put it at the same level
    # than the generic config (as name, type,...)
    for fieldCfg in cfgModule['fields']:
      # Put all the field's config at the first level
      if 'config' in fieldCfg: 
        if fieldCfg['type'] in fieldCfg['config']:
          fieldCfg.update(fieldCfg['config'][fieldCfg['type']])
        else:
          fieldCfg.update(fieldCfg['config'])
          
      # By default, the fields are NOT transient
      if 'transient' not in fieldCfg:
        fieldCfg['transient'] = False
      # By default, the fields are NOT readOnly
      if not 'readOnly' in fieldCfg:
        fieldCfg['readOnly'] = False
      # By default, the fields are NOT hide
      if not 'hide' in fieldCfg:
        fieldCfg['hide'] = False
      # In case of FK, the relation can be:
      # + association (default)
      # + aggregation 
      if fieldCfg['type']=='FK':
        # Check the relationType
        if 'relationType' in fieldCfg:
          if fieldCfg['relationType']!='association' and fieldCfg['relationType']!='aggregation':
            raise "Unknow relationType '{relationType}'".format(**fieldCfg) 
        # Set default relationType
        else: 
          fieldCfg['relationType']='association'
      # Check format is defined    
      elif fieldCfg['type']=='Date' or fieldCfg['type']=='DateTime':
        if not 'format' in fieldCfg:
          raise Exception('Missing "format" for field {name} of type {type}'.format(**fieldCfg))
        # Check the date format : 
        # In the JSON we set the format in a "neutral" way that afterwards need
        # to be translated to PHP, JAVA, JS, .... Because we are not going
        # to implement a full "date format" parser, we will allow only some
        # formats     
        format=fieldCfg['format']
        dateFormatEquivalence=self.getDateFormatEquivalences()
        # We have fo perform the equivalence
        if dateFormatEquivalence:
          if format not in dateFormatEquivalence:
            raise Exception('Unknown format {format} for field {name} of type {type}'.format(**fieldCfg))
          # Put the equivalance Date/DateTime
          fieldCfg['formatEquivalent'] = dateFormatEquivalence[format]
        
        # By default, show the calendar
        if 'showCalendar' not in fieldCfg:
          fieldCfg['showCalendar'] = True
             
    # -------------------------------------------------- Create element 'actions'
    # 'actions', be sure we have a value 
    if not 'actions' in cfgModule:
      cfgModule.update({'actions' : []})
    # 'actions' can be an empty dictionary!
    elif isinstance(cfgModule['actions'], dict) and not bool(dict(cfgModule['actions'])):
      cfgModule['actions'] = list()

    # [START] ---------------------------------------------- Add Default Actions
    # Generate some defalt actions if specified (opt --genDefaultActions)
    if genDefaultActions:
      # ListAll
      if not utils.search_dictionaries('name', 'ListAll', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'ListAll', 
          'type' : 'list',
          'globalActions' : [
            { "module" : moduleName, "name" : "AddAll", "params" : []}
          ]
        }) 
  
      # ModAll
      if not utils.search_dictionaries('name', 'ModAll', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'ModAll',
          'type' : 'mod'
        }) 

      # AddAll
      if not utils.search_dictionaries('name', 'AddAll', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'AddAll', 
          'type' : 'add'
        }) 

      # ViewAll
      if not utils.search_dictionaries('name', 'ViewAll', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'ViewAll', 
          'type' : 'view', 
          'globalActions' : [
            { 
              "module" : moduleName, 
              "name" : "DelAll", 
              "params" : [ 
                { "name" : "Id", "value" : "$Id" }
              ]
            },
            { 
              "module" : moduleName, 
              "name" : "ModAll",
              "params" : [ 
                { "name" : "Id", "value" : "$Id" }
              ]
            }
          ]
        }) 

      # Del
      if not utils.search_dictionaries('name', 'Del', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'DelAll', 
          'type' : 'del',
          'beOnly' : True,
          'askConfirmation' : True,
          'goOnActionDone' : 'back'
        }) 

      # Load
      if not utils.search_dictionaries('name', 'Load', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'Load', 
          'type' : 'load'
        }) 

      # Import
      if not utils.search_dictionaries('name', 'Import', cfgModule['actions']):
        cfgModule['actions'].append({ 
          'name' : 'Import', 
          'type' : 'import'
        }) 
    # [END] ------------------------------------------------ Add Default Actions

    # [START] ----------------------------------------- Review all the 'actions'
    for actionCfg in cfgModule['actions']:
      # IL - 08/04/15 - The JSON has changed, perform some checks to ensure we
      # use the rigth configuration
      if 'filter' in actionCfg:
        raise Exception('OLD configuration not allowed (now use params instead filter')

      # Set this action permission if not already defind
      if not 'permission' in actionCfg:
        # Defined at module level  
        if 'permission' in cfgModule:
          actionCfg['permission']=cfgModule['permission']
        # Default permission MODULE:ActioName 
        else:  
          actionCfg['permission']=moduleName + ":" + actionCfg['name']

      # By default, the actions are not beOnly except Load and Del
      if not 'beOnly' in actionCfg:
        if actionCfg['type']=='del' or actionCfg['type']=='load':
          actionCfg['beOnly']=True
        else:
          actionCfg['beOnly']=False
          
      # By default, the actions are not feOnly except composed/dashboard
      if not 'feOnly' in actionCfg:
        if actionCfg['type']=='composed' or actionCfg['type']=='dashboard':
          actionCfg['feOnly']=True
        else:
          actionCfg['feOnly']=False

      # By default, NO ask confirmation when performing an action, except del 
      if not 'askConfirmation' in actionCfg:
        if actionCfg['type']=='del':
          actionCfg['askConfirmation']=True
        else:  
          actionCfg['askConfirmation']=False

      # By default, after an action is done we go back 
      if not 'goOnActionDone' in actionCfg:
        actionCfg['goOnActionDone']='back'

      # ------------------------------------------------------------ itemActions
      if 'itemActions' in actionCfg:
        validStyles = ['onrow', 'outrow']

        for itemActionCfg in actionCfg['itemActions']:
          # By default, they are rendered in the row
          if not 'style' in itemActionCfg:
             itemActionCfg['style'] = validStyles[0]
          
          # Validate style
          if itemActionCfg['style'] not in validStyles:
            raise Exception('Unknown itemAction style "' + itemActionCfg['style'] + '" in ' + moduleName + ':' + actionCfg['name'] + '. Possible values are ' + ','.join(validStyles))

          # By default, once the item action is done, refresh the page
          # if not 'goOnActionDone' in itemActionCfg:
          #   itemActionCfg['goOnActionDone'] = 'refresh'

      # -------------------------------------------------- 'fields' in 'actions'
      # Add all fields if not defined
      if 'fields' not in actionCfg:
        actionCfg['fields'] = cfgModule['fields']
      # Complete the field info refered in actions
      else:
        # Reorganize some info so it is easier to access to it. 
        for fieldCfg in actionCfg['fields']:
          if 'config' in fieldCfg and fieldCfg['type'] in fieldCfg['config']:
            fieldCfg.update(fieldCfg['config'][fieldCfg['type']])

        # Update with the missing info coming from the general definition    
        self.completeFieldInfo(actionCfg['fields'], cfgModule['fields'])

      # -------------------------------------------------- 'params' in 'actions'
      # Complete the field info refered params
      if 'params' in actionCfg:
        self.completeFieldInfo(actionCfg['params'], cfgModule['fields'])

      # Lists
      if actionCfg['type']=='list':
        # ----------------------------------------------- 'listFilter' for lists
        # Create listFilter if it does not exist
        # If exists it can be None (null) and that means we do not want filter
        if 'listFilter' not in actionCfg:
          # CAREFUL : do not add those fields that are already a param
          if 'params' in actionCfg:
            actionCfg['listFilter']=[]

            # Loop over all the fields; we will add those thare are NOT in 'params'
            for fieldCfg in actionCfg['fields']:
              # This field does NOT exist in the list of params => Add it
              if not utils.search_dictionaries('name', fieldCfg['name'], actionCfg['params']):
                actionCfg['listFilter'].append(fieldCfg)
              # Do not add
              else:
                pass
                # print "Removing field {name} form filter!".format(**fieldCfg)
          # Add all the fields as listFilter
          else:
            actionCfg['listFilter'] = actionCfg['fields']

        # Complete the field info refered 'listFilter'
        if actionCfg['listFilter']:
          self.completeFieldInfo(actionCfg['listFilter'], cfgModule['fields'])

        # Review listFilter    
        # If None (null in the JSON) , we do not have filter
        if actionCfg['listFilter']:
          for fieldCfg in actionCfg['listFilter']:
            # Default value for operator
            if 'operator' not in fieldCfg:
              fieldCfg['operator'] = '=' if fieldCfg['type']=='FK' else 'LIKE'    

        # -------------------------------------------------- 'onClick' for lists
        # Add action ViewAll
        if 'onClick' not in actionCfg:
          actionCfg['onClick'] = {
            "module" : moduleName,
            "actionName" : "ViewAll",
            "params" : [
              { "name" : "Id", "value" : "$Id" }
            ]
          }

        # ------------------------------------------------- 'printDoc' for lists
        # By default, disable printDoc in lists
        if 'printDoc' not in actionCfg:
          actionCfg['printDoc'] = False

        # ------------------------------------------------- 'printDoc' for lists
        # By default show 10 records
        if 'totPerPage' not in actionCfg:
          actionCfg['totPerPage'] = 10
      # View
      elif actionCfg['type']=='view':
        for fieldCfg in actionCfg['fields']:
          if 'indCol' not in fieldCfg:
            fieldCfg['indCol']=0
      # Import
      elif actionCfg['type']=='import':
        actionName=actionCfg['name']
        if not 'transformer' in actionCfg:
          raise Exception('Old configuration in {moduleName} : Import action with name "{actionName}" does not have transdformeres inside'.format(**locals()))

      # -------------------------------------------------- 'config' in 'actions'
      # Reorganize some info so it is easier to access to it
      # @TODO : Is this used? Do the actions have a 'cfg'? What is used for?
      if 'config' in actionCfg:
        # @TODO : Unify the tow ways of setting the configuration
        if actionCfg['type'] in actionCfg['config']:
          actionCfg.update(actionCfg['config'][actionCfg['type']])
        else:
          actionCfg.update(actionCfg['config'])

      # ---------------------------------------------------------- checkSecurity
      # The FE will call to the server ALWAYS to check if the user has access to
      # a certain action or not in order to render the button. 
      # This will INCREASE the traffic with the BE, but if it represents a problem
      # we can call the the BE to check ONLY those actions that has been 
      # EXPLICITLY marked (see php2js.js for +info)
      if 'checkSecurity' not in actionCfg:
        # @TODO : decide what to do with this actions, it is not very clear
        # which code must be performed at server side  
        if actionCfg['type']=='view' or actionCfg['type']=='list' or actionCfg['type']=='composed' or actionCfg['type']=='dashboard':
          pass
        else:
          # Here we configure the class that will be executed
          # in the server to check a certain's action permission
          actionCfg['checkSecurity'] = {
            "module" : moduleName,
            "name" : actionCfg['name']
          }
          # Add the params, that are the same that the action
          if 'params' in actionCfg:
            actionCfg['checkSecurity']['params']=[]
            for paramCfg in actionCfg['params']:
              actionCfg['checkSecurity']['params'].append({
                "name" : paramCfg['name'],
                "value" : "$" +  paramCfg['name']
              })

      # ------------------------------------------------------------ loadDataURL
      # Create a default load loadDataURL for some actions
      # @TODO : should we do for all the actions?
      if 'loadDataURL' not in actionCfg:
        if actionCfg['type']=='mod' or actionCfg['type']=='view':
          actionCfg['loadDataURL'] = {
            "module" : moduleName,
            "name" : "Load"
          }
          # The action's params determine the params for the load action
          if 'params' in actionCfg:
            actionCfg['loadDataURL']['params'] = []
            for paramCfg in actionCfg['params']:
              paramName = paramCfg['name']
              paramValue = '$' + paramCfg['name'] if 'value' not in paramCfg else paramCfg['value']
              actionCfg['loadDataURL']['params'].append({
                'name' : paramName,
                'value' : paramValue 
              })

      # --------------------------------------------------------------- Composed
      # For the composed pages, if nothing is specified, the first panel is
      # NOT collapsable an the other are
      if actionCfg['type']=='composed':
        ind=0
        # Loop over all the actions
        for sectionCfg in actionCfg['sections']:
          # By default, the style is tabbed if there is MORE that one
          if 'style' not in sectionCfg:
            sectionCfg['style'] = 'tabPanel' if len(sectionCfg['actions'])>1 else "flow"
          else:
            validStyles = ['tabPanel', 'flow'] 
            if sectionCfg['style'] not in validStyles:
              raise Exception('Unknown composed style "' + sectionCfg['style'] + '" in ' + moduleName + ':' + actionCfg['name'] + '. Possible values are ' + ','.join(validStyles))
          for sectionActionCfg in sectionCfg['actions']:            
            # collapsable is we allow that a certain section CAN be collapsed.
            # by default we allow all to be
            if 'collapsable' not in sectionActionCfg:
                sectionActionCfg['collapsable']=True

            # collapsed is if INITAILLY is show collapsed
            # by default all are shown NOT collapsed
            if 'collapsed' not in sectionActionCfg:
                sectionActionCfg['collapsed']=False

            # No label defined
            if 'label' not in sectionActionCfg:
              sectionActionCfg['label'] = '{module}:{name}:Title'.format(**sectionActionCfg)
              
      # If is not a componed, never collapsable
      else: 
        if 'collapsable' not in actionCfg:
          actionCfg['collapsable']=False
        if 'collapsed' not in actionCfg:
          actionCfg['collapsed']=False

    # [END] ------------------------------------------- Review all the 'actions'
      
  # We have the following problem processing the CUSTOM files.:
  # Let's suppose we have written custom code for the action ListAll. 
  # When we process the custom file, because this is not a tmpl, we do not
  # have access to all the config for this action.
  # Build a map with:
  # key : destination file
  # NOTE : I know this function contains some code that is executed again later,
  # but this is the best way to introduce this change maintaning the existing code.  
  def _buildFilesConfig(self):
    # Skip if we do not have to do
    if 'actions' not in self.cfgModule or not self.options.dirTmpls: return

    # Set this value needed by 'getDstPath'
    self.baseDstDir=self.options.destination

    # Step1> Loop over all the files containing templates so we build 'listTemplates' 
    # key : actionType
    # value : array of objects:
    #   {
    #     'srcFile' : like /home/ilegido/projects/webrad/templates/Module/FE/SOOCSS/{ActionName}{MODULE}.html.mod.tmpl
    #     'dstFile' : like /home/ilegido/projects/webrad/build/fe/_User/./{ActionName}{MODULE}.html
    #   }
    listTemplates={}

    # Loop recursive all the files in the list of directories where there 
    # are the templates
    for dirTmpl in self.options.dirTmpls.split(','):
      # Set this value needed by 'getDstPath'
      self.templateDir=dirTmpl
      
      for (path, dirs, files) in os.walk(dirTmpl):              
        for file in files:
          srcFile=os.path.join(path,file)
          if srcFile.endswith('.tmpl'):
            dstFile=self.getDstPath(srcFile)
            match = self.tmplFilesPattern.match(dstFile)
            if match:
              newDstFile = match.group(1) # The real file name, without '.<action>.tmpl'                    
              actionType = match.group(2)

              if not actionType in listTemplates:
                listTemplates[actionType] = list()

              listTemplates[actionType].append({
                'srcFile' : srcFile,
                'dstFile' : newDstFile
              })            

    if False:
      for action in listTemplates:
        print """
[{action}]""".format(**locals())
        for row in listTemplates[action]:
          print """
  srcFile : {srcFile}
  dstFile : {dstFile}
""".format(**row)

    # Step2> Loop over all the 'actions'. For every action:
    # - Search in the previous dictionary
    # - Get all the templates and generate the final files
    # The result is a dictionary: 
    # key : destination file
    # value : the config used
    filesConfig=[]
    for actionCfg in self.cfgModule['actions']:
      actionType=actionCfg['type']
      self.currentItemCfg=actionCfg

      # Not always listTemplates[actionType] will be defined. Fex. in 'actions'
      # we can have an action of type 'view' and when processing the templates for 
      # PHP, ther is NO template 'view'.       
      if actionType in listTemplates:
        # For that action, loop over all the templates we have found before
        for template in listTemplates[actionType]:
          # Compute the expected destination files
          finalDstFile = self.getDstPath(template['dstFile'])
          # print ">>> {actionType} : {finalDstFile}".format(**locals())
          filesConfig.append({
            'file' : finalDstFile,
            'cfg' : actionCfg
          })

    return filesConfig

  # Raise an exception and provides info about where has been produced
  def _raiseException(self, msg):
    moduleName = self.moduleName
    actionName = self.currentItemCfg['name']
    
    raise Exception("""
================================================================================
Error in {moduleName}:{actionName}
{msg}
================================================================================""".format(**locals()))

  # ============================================================================
  # Overwrite
  # ============================================================================
 
  # Returns the name of the expected destination file (or folder) giving the sorce one
  # In this overwrite, we take into account the tmpl files
  def getDstPath(self, srcPath):
    # print ">>> getDstPath(" + srcPath + ")"
    # In case of the tmpl files we are not able to resolve the variables in the 
    # name
    # @TODO : use pattern instead!
    if srcPath.endswith('.tmpl') or srcPath.endswith('.inc'):
      return ResolverWebrad.getDstPath(self, srcPath, False)
    # No template, just default
    else:
      return ResolverWebrad.getDstPath(self, srcPath)

  def resolveDir(self, templateDir, baseDstDir):
    # Run the parent method. In this case, because we have overwritten the method
    # genFileFromTmpl, the template files have NOT been transformed
    ResolverWebrad.resolveDir(self, templateDir, baseDstDir)

    # Ok, now we have to take care of the template files

    # Loop over all the possible actions defined in the config file (usually
    # we should have defined at least some default actions)

    if 'actions' in self.cfgModule:
      #--- print "Found " + str(len(self.cfgModule['actions'])) + " actions"
      #--- for actionCfg in self.cfgModule['actions']:
      #---   print "DUMP ACTION"
      #---   print (json.dumps(actionCfg))
      #--- sys.exit(0)

      for actionCfg in self.cfgModule['actions']:
        if not 'type' in actionCfg:
          raise Exception("No key 'type' found in cfg : " + json.dumps(actionCfg))
  
        # This is the action type (list, add, mod, ...)
        actionType = actionCfg['type']

        # We have a template for that action type.
        # This could be an error BUT there can be situations (like when updating a 
        # module) that is not te case, so we will ignore
        if not actionType in self.listTemplates:
          pass
        # Skip if this file (do NOT generate and output) if:
        # + It is marked ass feOnly and this Resolver is for BE
        # + It is marked ass deOnly and this Resolver is for FE
        elif actionCfg['feOnly'] and self.isBEResolver() or actionCfg['beOnly'] and self.isFEResolver():
          pass
        else:
          # Ok, now generate the file using the right template
          self.currentItemCfg = actionCfg
          # Generate with this cfg the forms
          for tmpl in self.listTemplates[actionType]:
            srcFile = tmpl['srcFile']
            dstFile = ResolverWebrad.getDstPath(self,tmpl['dstFile'])
            # print ">>>> Generate {srcFile} => {dstFile}".format(**locals())
            ResolverWebrad.genFileFromTmpl(self, 
              srcFile,     
              dstFile
            )
          # end loop tmpl
  
  # Overwirtten to have into account the .tmpl files. At this point we do not 
  # generate but keep all the .tmpl files related with a certain action
  def genFileFromTmpl(self, srcFile, dstFile, itemCfg=None):
    # print ">>> genFileFromTmpl({srcFile}, {dstFile})".format(**locals())

    # If this files is a template related with a certain action (see comment in
    # self.listTemplates) we keep it in a dictionary and we will generate 
    # afterwards 
    # Before it wasos.path.basename(dstFile).endswith(".tmpl") but now dstFile can 
    # be None and I THINK it can be cecheck agains srcFile 
    if dstFile and os.path.basename(srcFile).endswith(".tmpl"):
      if os.path.basename(srcFile)=='lang.properties.tmpl':
        raise Exception("Please review your code, lang.properties.tmpl is not used anymore!!!")
      else:
        # print ">>> genFileFromTmpl. Is Tmpl"
        # Get the action (the file should follow the patter <name>.<action>.tmpl)
        match = self.tmplFilesPattern.match(srcFile)
        if not match:
          raise Exception("Invalid pattern for tmpl file : " + srcFile)

        newDstFile = match.group(1) # The real file name, without '.<action>.tmpl'                    
        actionType = match.group(2)
        
        # Create an empty list to store data for that action type
        if not actionType in self.listTemplates:
          self.listTemplates[actionType] = list()
        
        # In this case, we only need te srcFIle, because the dstFile is not going 
        # toAppend this file to the list related with this action type
        # Fex. for actionType='list' we can have
        # srcFile : templates/PHPModule/views/{ActionName}{MODULE}.php.list.tmpl
        # dstFile : demo1/www/Voter/views/{ActionName}{MODULE}.php
        self.listTemplates[actionType].append({
          'srcFile' : srcFile,
          'dstFile' : newDstFile
        })                       
    # No template, use the default implementation
    else:
      # Just in case we have set previously a value, so avoid to reuse it
      self.currentItemCfg = None
      if self.filesConfig:
        # Is this a generated file from a template? Can we get the config used?
        foundCfg = utils.search_dictionaries('file', dstFile, self.filesConfig)
        # We have the config, set it as value and generate the file
        if foundCfg:
          self.currentItemCfg = foundCfg['cfg']

      # Resolve the file    
      return ResolverWebrad.genFileFromTmpl(self, srcFile, dstFile, itemCfg)
    
  # Returns the config related with a certain module:action
  def _getActionCfg(self, moduleName, actionName):
    cfgAction = utils.search_dictionaries('name', actionName, self.allModulesConfig[moduleName]['actions']) 

    if not cfgAction:
      raise Exception("No action {actionName} found in {moduleName}.".format(**locals()))
  
    return cfgAction
    
  def isBEResolver(self):
    raise Exception("This method should be overwritten!")

  def isFEResolver(self):
    raise Exception("This method should be overwritten!")

  # In the JSON de daat formats are expressed in a "neutral" way (the Java
  # format is used) but then need to be translated in the one understood
  # by PHP, Java, JS,... so, those variables will be translated by the
  # ResolverXXX
  def getDateFormatEquivalences(self):
    return None

  # ============================================================================
  # Test functions for conditional contents
  # ============================================================================
  def printTestOutputBreadrumb(self):
    return "True"  
      
  # ============================================================================
  # Replacement generic
  # ============================================================================

  # -------------------------------------------
  # Functions
  # -------------------------------------------

  # -------------------------------------------
  # General
  # -------------------------------------------
  
  # $BeanName
  def printBeanName(self):
    return self.moduleName 

  # Module Name
  def printMODULE(self):
    return self.moduleName 

  # $beanName
  # lowercase the first
  def printbeanName(self):
    return self.moduleName[:1].lower() + self.moduleName[1:]

  def printAPP_NAME(self):
    return self.cfgModule['values']['prjName']

  # ============================================================================
  # Replacement depending on the action
  # ============================================================================

  def IsPropertyDefined(self, propName, propValue=None):
    retVal=""

    if propName in self.currentItemCfg:
      if propValue:
        if self.currentItemCfg[propName]==propValue:
          retVal = "OK"
      else:
        if self.currentItemCfg[propName]:
          retVal = "OK"

    return retVal
        
  # {ActionName}
  # The action name, used also for the file names
  def printActionName(self): 
    if not self.currentItemCfg:
      print "WARNING. currentItemCfg not set when processinf " + self.currSrcFile
    return self.currentItemCfg['name']
    #return "" if not self.currentItemCfg else self.currentItemCfg['name']

  # {PermissionName}
  # The action name, used also for the file names
  def printPermissionName(self): 
    return self._getPermission(self.currentItemCfg, self.cfgModule, self.moduleName)

  # {BreadcrumbTitle}
  # Text for the Breadcumb. At this moment is just the Title used in the page 
  # (<Module>:<Action>:<Title>)
  def printBreadcrumbTitle(self):
    return self.moduleName + ":" +  self.currentItemCfg['name'] + ":Title"     

  # ---------------------------------------------------------- Private Functions   
  def _getPermission(self, actionCfg, moduleCfg, moduleName):
    return actionCfg['permission']  
