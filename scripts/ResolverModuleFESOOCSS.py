#!/usr/bin/python
# -------------------------------------------
# Resolver spedific for modules PHP
# @TODO: Do not overwrite not generate files (those that do not start with _)
# -------------------------------------------
import re
import os
import sys
import pprint
import json
import copy
import utils
import importlib
from Resolver import Resolver
from ResolverModule import ResolverModule
from ResolverWebrad import ResolverWebrad

class ResolverModuleFESOOCSS(ResolverModule):

  def __init__(self, moduleName, cfgModule, options):
    ResolverModule.__init__(self, moduleName, cfgModule, options)
    # This counter allows to create unique identifier for HTML element but not
    # random 
    self.counter = 0
    # Used to avoid the output of several startHTML/endHTML blocks when generating
    # composed pages
    self.generateStartHTML = True
    self.generateEndHTML = True


  def isBEResolver(self):
    return False

  def isFEResolver(self):
    return True

  # The conversors between the date format used in the JSON and JS (jquery 
  # datapicker )
  # @TODO : datepicker does not support time
  def getDateFormatEquivalences(self):
    return {
      'dd/MM/yy' : 'dd/mm/yy',
      'MM/dd/yy' : 'mm/dd/yy',
      'dd/MM/yy HH:mm' : 'dd/m/Y',
      'MM/dd/yy HH:mm' : 'm/d/Y'
    }  

  # ============================================================================
  # Private Methods
  # ============================================================================
 
  # Using serie or parameters, build the query string
  # @param params Array onbjects {"name" : ...., "value" : ....} where
  #               - name : param name that will be added in the query string
  #               - value : value assigned to the param. If it starts with $ that
  #                 means is a run-time value that must be extracted from an array
  #                 (see nameArrayWithValues); otherwise is a literal
  # @param nameArrayWithValues Name of the array where the run-time values are 
  #                            stored
  # @param nameFunctionWithValues Same than array but a function
  #
  # Fex:
  #   _buildQueryString( 
  #     [ 
  #        {"name" : "Id",     "value" : "$IdParent"}, 
  #        {"name" : "IdZone", "value" : "3" } 
  #     ], 
  #     "urlParams"
  #   )
  # will return
  #   'Id=' + urlParams['IdParent'] + '&IdZone=' + '3'
  def _buildQueryString(self,params, nameArrayWithValues, nameFunctionWithValues=None):
    if not params:
      return ""

    buff=""
    # Loop over all the params to build the query string
    for paramCfg in params:
      name  = paramCfg['name']
      value = paramCfg['value']
      
      # Separator
      if len(buff)>0:
        buff += " + "
        sep="&"
      else:
        sep=""

      # Param name
      buff += "'{sep}{name}='".format(**locals())

      # Param value
      # Run-time value, we have to extract it from the array containing the 
      # values
      if value and len(value)>1 and value[0]=='$':
        key=value[1:]
        if nameFunctionWithValues:
          buff += " + encodeURIComponent({nameFunctionWithValues}('{key}'))".format(**locals())
        else:
          buff += " + encodeURIComponent({nameArrayWithValues}['{key}'])".format(**locals())
      # Literal
      else:
        buff += " + encodeURI('{value}')".format(**locals())   

    return buff   

  # Return the URL for a certain action 
  # @TODO : unify all the calls to this method, so it can return a string with the 
  # params (there is some differences if it must return just the string or a quoted one...)
  def _getActionUrl(self, moduleName, actionName):
    # Get the configuration form that module:action
    cfgAction = self._getActionCfg(moduleName, actionName)

    # It is a BE only
    if cfgAction['beOnly']:
      return self.urlBE('/service/{moduleName}/service/{actionName}{moduleName}'.format(**locals()))
    # Default action (FE)
    else:
      return self.urlFE('/{moduleName}/{actionName}{moduleName}.html'.format(**locals()))

  # Array of actions (Gloabl, Item,....)
  # We return an array of objects that allow, using renderData(), to dynamically
  # create so many buttons as actions defined
  # There are some differences in the code if it is used to generate itemActions
  # or globalActions, see comments below
  def _buildArrayActions(self, cfgActions, nameArrayWithValues="globalActionsData", isGlobalActions=True):
    buff=""

    for cfg in cfgActions:
      moduleName=cfg['module']
      actionName=cfg['name']
    
      # -------------------------------------------------------- URL with Params
      # URL for that action. Depending on the action can go to a new page (default)
      # or execute a service
      url = self._getActionUrl(moduleName, actionName)

      # Now build the query for that url

      # Params declared in the JSON file for the remote action
      if 'params' in cfg:
        queryParams = cfg['params']
      # No params defined 
      else:
        queryParams = [] 
        
      # Obtain the query string for that query params
      query = self._buildQueryString(queryParams, nameArrayWithValues)

      # Full URL
      if len(query)>0:
        fullquery = "'{url}?' + {query}".format(**locals())
      else:
        fullquery = "'{url}'".format(**locals())

      if len(buff)>0: buff += ","

      # ------------------------------------------------------- Other Attributes
      # Add the action that will be rendered as a button
      # The action's label
      i18nActionLabel = self.i18n("{moduleName}:{actionName}:Button".format(**locals()))

      # cfgAction is the full configuration od the "remote action"      
      cfgAction = self._getActionCfg(moduleName, actionName)
      # Update with some things that maybe we have defined when calling this 
      # action. 
      # @TODO : We do not do a full update here because I'm not sure how is 
      # going with the params, so I will "cherry pick"
      if 'goOnActionDone' in cfg:
        cfgAction['goOnActionDone'] = cfg['goOnActionDone']       

      # Check if this action requires a confirmation or not
      if cfgAction['askConfirmation']:
        i18nAskConfirmation=self.i18n("{moduleName}:{actionName}:AskConfirmation".format(**locals()))
      else:
        i18nAskConfirmation=""

      beOnly = "true" if cfgAction['beOnly'] else "false"
      permission = cfgAction['permission']
      goOnActionDone = cfgAction['goOnActionDone']
      paramsAsJson = json.dumps(queryParams)

      # ---------------------------------------------------------- CheckSecurity
      # There is a runtime check (aditional to permission) to check it this
      # action can be performed or not 
      if 'checkSecurity' in cfgAction and cfgAction['checkSecurity'] and cfgAction['checkSecurity']:
        # cfgAction['checkSecurity']['params'] will contain values to the 
        # parameters that need to be 'evaluated'.

        # Ok, take breath because what follows is not an easy piece of code :-)
        # First, the sitaution is the following: we are processing an action
        # (fex. Candidate:ViewAll) that refers to another (fex. via globalActions
        # to CandidateLog:AddByWorkflow ) that has a security check
        # * cfg : is the configuration of the main action (the 'local') =>  Candidate:ViewAll
        # * cfgAction : is the configurtion of the referred action (the 'remote') => CandidateLog:AddByWorkflow
        # What we're trying to solve is the following:
        # * the local receives as param 'Id' (that represents the Id of the Candidate)
        # * the remote receives as param 'IdCandidate' and the checkSecurity needs a 
        #   parameter IdCandidate which value is $IdCandidate because this is the name
        #   of the parameter in the action        
        # The point is that this IdCandidate need to be resolved locally as $Id         
        #
        # Because that was in fact very easy to understand :-), think about the 
        # situation when this function is used to render the itemActions in a 
        # list. There are some differences when using to render the globalActions:
        # + In the globalActions the source of data is widgetData['actionParams']
        #   but in the itemActions it change for every item
        # + When checking if when calling this actions it will be provided with 
        #   the right params, in globalActions we will check with the 'params'
        #   that is the parent in this globalAction (becuase it will provide the
        #   values for calling the globaAction) while in the itemActions is the 
        #   item list 

        checkSecurityAsString="{"
        checkSecurityAsString+='"module" : "{module}", "name" : "{name}"'.format(**cfgAction['checkSecurity'])
        if 'params' in cfgAction['checkSecurity']:
          if isGlobalActions and 'params' not in self.currentItemCfg:
            raise Exception('checkSecurity has params but the action has not ' + json.dumps(self.currentItemCfg))
  
          # We chave to produce an String because when processing the params 
          # we need to produce an expression like
          #   { "Id" : varData['Id'] }
          # so when executing the JS the expression varData['Id'] is evaluated
          # The problem is that processing paramCfg as array and replacing value
          # but such expressions we get things like
          #   { "Id" : "varData['Id']"" }
          # that is not we want
          paramsAsString=""

          # paramCfg are the params in the "remote" action
          for paramCfg in cfgAction['checkSecurity']['params']:
            if len(paramsAsString)>0: paramsAsString += ","

            paramName=paramCfg['name']
            # It has reference to a runtime value (the normal)
            if paramCfg['value'][0]=='$':
              varName=paramCfg['value'][1:]
              # Ok we have to know how this variable $...
              # is translated in the context of the 'local' action

              # Search varName in the list of params
              paramDef = utils.search_dictionaries('name', varName , cfg['params'])  
              if not paramDef:
                # The action has defined a param but are not able to provide a
                # value
                print json.dumps(cfgAction['checkSecurity'],indent=4)
                raise Exception("""

ERROR ===================================================                  
{thisModuleName}:{thisActionName}
Error processing the action {moduleName}:{actionName}
The variable {varName} was not found in the list of params 
==========================================================""".format(thisModuleName=self.moduleName, thisActionName=self.currentItemCfg['name'],moduleName=moduleName,actionName=actionName,varName=varName))                  
              
              # We provide a value
              if 'value' in paramDef:
                # It self a variable
                if paramDef['value'][0]=='$':
                  paramValue=nameArrayWithValues + "['" + paramDef['value'][1:] + "']"            
                # Hardcoded
                else:
                  paramValue='"' + paramDef['value'] + '"'
              # This is a problem because we want to call a checkSecurity and not pass any value
              else:
                raise Exception("""

ERROR ===================================================                  
{thisModuleName}:{thisActionName}
Error processing the action {moduleName}:{actionName}
The variable {varName} has not defined a value 
==========================================================""".format(thisModuleName=self.moduleName, thisActionName=self.currentItemCfg['name'],moduleName=moduleName,actionName=actionName,varName=varName))                  

            # Hardcoded value
            else:
              paramValue='"' + paramCfg['value'] + '"'

            paramsAsString += '{{"{paramName}" : {paramValue}}}'.format(**locals())
          
          checkSecurityAsString+=',"params" : [{paramsAsString}]'.format(**locals())

        checkSecurityAsString += "}"
      else:
        checkSecurityAsString = "null" 
      

      buff += """
    {{
      "actionName" : "{actionName}",
      "params" : {paramsAsJson},
      "url"  : {fullquery},
      "name" : "{i18nActionLabel}".translate(),
      "askConfirmation" : "{i18nAskConfirmation}",
      "beOnly" : {beOnly},
      "permission" : "{permission}",
      "goOnActionDone" : "{goOnActionDone}",
      "checkSecurity" : {checkSecurityAsString} 
    }}""".format(**locals())

    return "[" + buff + "]"  

  # Return a new unique HTML identifier (not random)
  def _getNewUniqueHTMLId(self):
    self.counter = self.counter + 1

    return self.printCurrentWidgetID() + "_" + str(self.counter) 
  
  # Return the JS needed to retreieve a list from the server and fill the <select>
  # @TODO : for some aspects we do not have the "best solution" yet, so we have
  # done some approaches:
  # - What to do with BIG lists? In those cases probably a best select mechanism, as
  #   chained selects, instamt search.... For the moment, 10000 records are retrieved
  # @param eId the id form the element <select>
  # @param url the url to retrieve the data  
  # @param varData the config in the JSON containing the following attributes:
  # - fieldId (Optional)
  # - fieldName The name of the property which value is shown in the select
  # - params (optional)
  #
  # In relation with the params, where are the values obtained from? Those selects
  # are rendered in a widget, so all the values must come from widgetData instead
  # request params
  def _getJS4Select(self, eId, varData, is4Form=True):

    fieldId = 'Id' if not 'fieldId' in varData else varData['fieldId']
    fieldName = varData['fieldName']

    # We have to pass parameters that are a filter that need to be
    # applied to the list. The values are obtained from the widget's params
    filter="{}"
    if 'params' in varData:
      filter = self._params2Array(varData['params'],"widgetData['actionParams']")

    # IL - 25/04/15 - The FK's configuration has been 'reestructured', before
    # the config was:
    # - url
    # - className
    # - fieldName
    # and now is (more generic)
    # - module
    # - actionName
    # - fieldName
    # BUT we  still allow 'url' jsut in case data can be loaded from an 
    # external source 
    if 'url' in varData and 'className' in varData:
      raise Exception('Old configuration form FK (url, className) NOT allowed')    

    url=None
    # External URL @TODO : not really tested
    if 'url' in varData:  
      url =  varData['url']
    # The list is get from an action's module.
    # @TODO : now it is suposed the action is the type 'list', but in the 
    # future all the actions could be possible
    else:
      url=self.urlBE("/list/{module}/dao/{actionName}{module}".format(**varData))


    # @TODO (de los gordos)
    # There is a big problem with the value of totPerPage
    # - Small value : if we edit/add an entity with a FK, if we do not load all the possible values then 
    #   the needed value is not displayed
    # - Big value : we can receive A LOT of values (Mb of info)
    # This FK is used also in the filter forms.
    CurrentWidgetID=self.printCurrentWidgetID()
    # When widgetReady we have access to widgetData
    
    buff = """
<script>"""

    # FORMS : custom.dataLoaded : triggered by add/mod/view  in the form
    if is4Form:
      buff += """
$('#frm{CurrentWidgetID}').on('custom.dataLoaded', function(evt, formData, widgetData){{""".format(**locals())
    # LIST (search form) 
    else:
      buff += """
$(document).on('custom.ready', function(evt, widgetData){{""".format(**locals())

    buff += """
  // Build the list of options
  $.getJSON(
    "{url}", 
    {{ 
        "totPerPage" : 100, 
        "filter" : {filter} 
    }},
    function(data) {{
      var $eSelect = $('#{eId}');

      // Add an empty option
      var $emptyOption = $('<option/>');
      $eSelect.append($emptyOption);

      // The URLs of the services as ListXXX are pagged, so this is the reason why
      // we must call data.data to the get the list of values. 
      $.each(data.data, function(index, value) {{
        var $option = $('<option/>').attr('value',value['{fieldId}']).text(value['{fieldName}']);
        $option.data('values', value);
        $eSelect.append($option);
      }});
      // @TODO : Show a warning if the entire list has not loaded (data.totPages >1 )
      if ( data.totPages > 1 ) {{
       console.log("WARNING : not all data for {url} has been loaded, there arround " + (data.totPages-1)*data.totPerPage + " records missing.");
      }}

      // If we have set a default value, select it
      /*
      if ( $eSelect.attr('value') ) {{
        $eSelect.val($eSelect.attr('value')).change();
      }}
      */
      if ( $('#{eId}').data('originalValue') ) {{
        $eSelect.val($('#{eId}').data('originalValue')).change();
      }}
    }}
  );
}});
</script>
""".format(**locals())

    return buff

  # ============================================================================
  # 
  # Replacement Methods resolving functions 
  #
  # ============================================================================
  # These functions are called by FE pages that are in [appContext]/fe/[module], like
  # can be ListAll_User.html
  def urlBE(self,vars):
    return '../../be' + vars
    
  def urlFE(self, vars):
    return '..' + vars  

  # ============================================================================
  # 
  # Replacement Methods with no Templates
  # Reference to generic config as self.cfgModule['fields']
  #
  # ============================================================================

  # -------------------------------------------
  # General
  # -------------------------------------------
  
  # $VersionResolver
  def printVersionResolver(self):
    return "1.0" 

  # When generating composed pages, do not write only once the startHTML/endHTML
  def printstartHTML(self):
    return os.environ['START_HTML_FILE'] if self.generateStartHTML else ""

  # When generating composed pages, do not write only once the startHTML/endHTML
  def printendHTML(self):
    return os.environ['END_HTML_FILE'] if self.generateEndHTML else ""

  # Header for the widget
  def printstartWidgetHTML(self):
    return os.environ['START_WIDGET_HTML_FILE'] 

  # Footer for the Widget
  def printendWidgetHTML(self):
    return os.environ['END_WIDGET_HTML_FILE'] 

  def printNewWidgetID(self):
    Resolver.SHARED_COUNTER = Resolver.SHARED_COUNTER + 1
    return self.printCurrentWidgetID()

  def printCurrentWidgetID(self):
    return "Widget{id}".format(id=Resolver.SHARED_COUNTER)
 
  # ============================================================================
  # 
  # Replacement Methods with Templates
  # Reference self.currentItemCfg
  #
  # ============================================================================

  # -------------------------------------------
  # Generic
  # -------------------------------------------

  # {GlobalActions}
  def GlobalActions(self, varNameWithData):
    if 'globalActions' in self.currentItemCfg:
      return self._buildArrayActions(self.currentItemCfg['globalActions'], varNameWithData)
    else:
      return '[]'

  # {LoadDataURL}
  def printLoadDataURL(self):    
    # Specified a custom data loader
    if 'loadDataURL' not in self.currentItemCfg:
      raise Exception("No loadDataURL defined!")

    cfg = self.currentItemCfg['loadDataURL'] 
    baseUrl = self._getActionUrl ( cfg['module'], cfg['name'])

    if 'params' in cfg:
      query = self._buildQueryString(cfg['params'], 'widgetData["actionParams"]')
      return "'{baseUrl}?' + {query}".format(**locals())
    else:
      return "'{baseUrl}'".format(**locals())  

    # return self.urlBE("/service/{module}/service/{name}{module}".format(**self.currentItemCfg['loadDataURL']))

  # Return the custom HTML (mainly containg JS) por this file, if any 
  def printCustomHTML(self):
    # Problem : this function is 'fired' when we're processing the temmplates, but
    # the possible custom file is in custom, so we can try to "find" the related
    # custom file
    # For example, we can have:
    #   self.currSrcFile = ${PRJ_HOME}/templates/Module/FE/SOOCSS/{ActionName}{MODULE}.html.add.tmpl
    #   self.currDstFile = ${FE_DST_DIR}/_User/./AddAll_User.html
    # and the customHTML should be
    #   ${PRJ_HOME}/model/custom/ModuleCustom/FE/SOOCSS/_User/AddAll_User.html.js.inc
    # that COULD be calculated basically using currSrcFile and currDstFile BUT
    # @TODO : it is weird, but sometimes self.currDstFile is None when should 
    # have some value (maybe related with the composed pages??) so we will use 
    # moduleName and actioName instead currDstFile
    # dstFile=self.currDstFile
    # dstFile=os.path.abspath(self.currDstFile).replace("\\","/")
    # customHTMLPath = \
    #   prjHome + \
    #   "/model/custom/ModuleCustom/FE/" + \
    #   os.environ['FE_TYPE'] + \
    #   dstFile.replace(feDstDir, "") + \
    #   ".inc"
    
    # Compute the customHTMLPath
    # @TODO : probably the use of string operations is not the best idea, should
    # be better to manipulate paths in an abstract way (to avoid problems with 
    # path separators in the different operator systems). The problem is that
    # the library that maybe could be used (pathlib) is for version 3.4
    prjHome=os.path.abspath(os.environ['PRJ_HOME']).replace("\\","/")
    feDstDir=os.path.abspath(os.environ['FE_DST_DIR']).replace("\\","/")
    srcFile=os.path.abspath(self.currSrcFile).replace("\\","/")

    moduleName=self.moduleName
    actionName=self.currentItemCfg['name']
    customHTMLPath = \
      prjHome + \
      "/model/custom/ModuleCustom/FE/" + \
      os.environ['FE_TYPE'] + "/" + \
      moduleName + "/" + \
      actionName + moduleName + ".inc"

    if os.path.exists(customHTMLPath):
      return customHTMLPath 
    else:  
      return ""

  # Return the value for body/@id (<body id="{PageID}">)
  # @TODO : return a value based on the file name?
  def printPageID(self):
    if not self.currentItemCfg:
      raise Exception("No currentItemCfg")

    return self.moduleName + "_" + self.currentItemCfg['name']  

  # Return the value for body/@class (<body class="{PageClassname}">)
  def printPageClassname(self):
    if not self.currentItemCfg:
      raise Exception("No currentItemCfg")

    className=""

    # Public page
    if not self.currentItemCfg['permission']:
      return "isPublic"
    
    className += " action-" + self.currentItemCfg['type']
  
    return className

  def printIsPublic(self):
    if not self.currentItemCfg:
      raise Exception("No currentItemCfg")

    return "" if self.currentItemCfg['permission'] else "true"

  def printCollapsedClass(self):
    # Do not add anything, the panel will be shown as usual
    if not self.currentItemCfg or not self.currentItemCfg['collapsable']:
      return ""
    # The panel will be shown collapsed and with the possibility to be expanded
    elif self.currentItemCfg['collapsed']:
      return "collapsable"  
    # The panel will be shown expanded and with the possibility to be collapsed
    else:
      return "collapsable expanded"  

  # Where to go after an action (add/mo/...) is done
  def OnActionDoneURL(self, nameVarData=None):
    goOnActionDone = self.currentItemCfg['goOnActionDone']

    # It specify another action
    if type(goOnActionDone) is dict:
      url = self._getActionUrl(goOnActionDone['module'], goOnActionDone['name'])

      if 'params' in goOnActionDone:
        queryParams = goOnActionDone['params']
      # No params defined 
      else:
        queryParams = [] 
        
      # Obtain the query string for that query params
      query = self._buildQueryString(queryParams,  nameVarData)

      # Full URL
      if len(query)>0:
        fullquery = "'{url}?' + {query}".format(**locals())
      else:
        fullquery = "'{url}'".format(**locals())
    # String : back, refresh  
    else:
      if goOnActionDone=='back':
        fullquery = "document.referrer"
      # Default, refresh current page
      else:
        fullquery = "document.location.href"
      
    return fullquery     
    # return "updateURLParameter({fullquery}, 'msgCode', '{i18nOnActionDone}')".format(**locals())   

  # -------------------------------------------
  # views/_{ActionName}{MODULE}.php.add.tmpl
  # views/_{ActionName}{MODULE}.php.mod.tmpl
  # Form to add/mod an item
  # -------------------------------------------

  def printFormFieldsNoI18N(self):
    return self._genInputEle4ListFields(self.currentItemCfg['fields'])

  # {ActionParamsAsObject}
  # Return the params defined for that action with the values, so some default
  # values can be set in the add/mod forms (fex. when creating a child element)
  # the parent element should be set (this method is somehow related to 
  # _buildQueryString)
  # @TODO : Maybe this can be done in the FE to see the value BUT the real value
  # should be set in the BE ignoring the data coming from the FE .... if this
  # value is not allowed to be changed .... hmmm, not an easy question ....
  def printActionParamsAsObject(self):  
    self._raiseException("""
You're using       

{ActionParamsAsObject}

but during the "autumn cleaning" is gone. It had two main problems:
+ Use duplicated code that was used in other functions
+ Get the param values from the request instead the widgetData. 

Please, change your call by

{ActionParamsObject(widgetData['actionParams'])}

and be sure widgetData is accessible in your code""")

  # ------------------------------------------------------------ Private methods
  # Given an array of params (fex. the action's params), return an object with 
  # all the the params and expression to get the values
  # @param params Array of params of the form [ { "name" : paramNamee [, "value" : paramValue]},...]
  def _params2Array(self, params, dataVarName,useRuntimeValuesIfPresent=True):

    buff = ""

    for item in params:
      sep = "" if len(buff)==0 else ","
      name=item['name']

      # No 'value' defined in params, so the value comes from dataVarName
      if 'value' not in item:
        buff += """
      {sep}'{name}' : {dataVarName}['{name}']""".format(**locals())
      # 'value' defined in params but if is NOT a literal, the values comes from
      # dataVarName
      elif item['value'] and len(item['value'])>1 and item['value'][0]=='$':
        if useRuntimeValuesIfPresent: 
          value=item['value'][1:]
        else:
          value=item['name']
          
        buff += """
      {sep}'{name}': {dataVarName}['{value}']""".format(**locals())
      # Literal value
      else:
        value=item['value']
        buff += """
      {sep}'{name}': '{value}'""".format(**locals())

    return "{" + buff + "}"
 
  # For a list of field, generate all the input elements
  def _genInputEle4ListFields(self, fields):
    buff=""
    for varData in fields:
      buff += self._genInputForm4OneField(varData)

    return buff

  # Generate the input field for a single field
  # This is a recursive function
  def _genInputForm4OneField(self, varData):
    buff=""

    moduleName = self.moduleName
    fieldName = varData['name']
    attrRequired = "required" if 'required' in varData and varData['required'] else ""

    # If this fields allows repetition, we have to create a _template 
    # to handle it
    isRepeatedField = 'repeat' in varData and varData['repeat']

    # Display?
    display = 'style="display:none;"' if 'hide' in varData and varData['hide'] else ' '
    
    # START : Composed Field
    # @TODO : Pending review with the new SOOCSS
    if varData['type']=='Object':
      buff += "<div class='{name}' data-jsonform-group='{name}' {display}>\n".format(name=varData['name'], display=display)
      # Group title
      i18nGroupTitle = self.i18n("{moduleName}:{fieldName}".format(**locals()))
      buff += """
      <div class="_i18n">{i18nGroupTitle}</div>""".format(**locals())
    # Regular field
    else:
      buff += """
      <!-- !regular-field -->
      <div class="col-xs-12 col-sm-4 {fieldName}" {display}>
        <!-- !form-group -->
        <div class='form-group {attrRequired}'>""".format(**locals())
      # Field's label
      i18nFieldLabel = self.i18n("{moduleName}:{fieldName}".format(**locals()))
      buff += """
          <label class='control-label _i18n'>{i18nFieldLabel}</label>""".format(**locals())

    # START : Repeated Field
    if isRepeatedField:
      buff += "<div class='_template'>\n"

    # START : Block surround the input (in case a non Object)
    # In the new SOOCSS there is no such block!
    # if varData['type']!='Object':
    #   buff += "<div class='col-sm-10'>"
    
    # Object Field
    if varData['type']=='Object':
      buff += self._genInputEle4ListFields(varData['fields'])
    # Display only
    # @TODO unify with _genViewEle4OneField?
    elif 'readOnly' in varData and varData['readOnly']:
      if varData['type']=='File':
        buff += "<a class='{name}URL'>{name}URL</a>\n".format(**varData)
      elif varData['type']=='Image':
        buff += "<img class='{name}URL' width='50px'></img>\n".format(**varData)
      elif varData['type']=='URL':
        buff += "<a class='{name}' href=''><span class='{name}'></span></a>\n".format(**varData)
      # In case of FK, do NOT show just the index but a "User Friendly" data 
      # (see param _completeFK when call the Load)
      elif varData['type']=='FK':
        buff += "<span class='{name}{fieldName}'/>".format(**varData)
      # For the bool, show the checkbox in readonly mode
      elif varData['type']=='Bool':
        buff += "<input type='checkbox' disabled readonly value='1' class='{name}'/>".format(**varData)
      else:
        buff += "<span class='{name}'/>".format(**varData)
    # Single input field. 
    # That means a input, select, ... where we are going to add validation attributes
    # according the definition. So in this first block we create the corresponding
    # input element ...
    else:
      # Foreign key to another Table. 
      # It depends if it is hide or not
      # - Not hide : We render it as a dropdown where we can select (Here we 
      #              render the HTML, the JS needed will be rendered later
      # - Hide : we render an input hide with the literal value, not a 'user 
      #          friendly' version. This is typical use when we create a
      #          dependent object and as param receives the Id of the parent
      if varData['type']=='FK':
        if varData['hide']:
          buff += "<input type='hidden'"
        else:  
          # Show a select with all the possible values
          if not 'chooseFromList' in varData or varData['chooseFromList']:
            eId = self._getNewUniqueHTMLId() 
            buff += "<select id='{eId}'".format(eId = eId)
          # @TODO : review, not clear when this is used ....
          else:
            buff += "<input type='hidden'"
      # Id from the parent class
      # @TODO : review & remove
      elif varData['type']=='ParentK':
        raise Exception("Unsupported type ParentK")
      # List of values
      # @TODO : review
      elif 'values' in varData:
        buff += "<select"
      elif varData['type']=='Bool':
        buff += "<input type='checkbox' value='1'"
      elif varData['type']=='Integer':
        buff += "<input type='number'"
        # Min/Max value if specified
        if 'min_val' in varData:
          buff += " min={min_val}".format(**varData)
        if 'max_val' in varData:  
          buff += " max={max_val}".format(**varData)
      elif varData['type']=='File' or varData['type']=='Image':
        jsonformFieldCfg={}
        # We're going to validate the file size
        if 'max_size' in varData:
          max_size=varData['max_size']
          i18nErrorTooBig="{moduleName}:{fieldName}ErrorTooBig".format(**locals())
          jsonformFieldCfg["max_size"] = { "value" : max_size, "error" : i18nErrorTooBig }

        # We're going to validate the file extensions
        if 'extensions' in varData:
          extensions=varData['extensions']
          i18nErrorWrongFileExtension="{moduleName}:{fieldName}ErrorWrongFileExtension".format(**locals())
          jsonformFieldCfg["extensions"] = { "value" : extensions, "error" : i18nErrorWrongFileExtension }
        
        buff += """
        <div class="form-control input-file">
          <input type='file' data-jsonform-fieldCfg='{jsonformFieldCfg}'
""".format(jsonformFieldCfg=json.dumps(jsonformFieldCfg))
      elif varData['type']=='Password':
        buff += "<input type='password'"
      elif varData['type']=='Email':
        buff += "<input type='email'"
      elif varData['type']=='URL':
        buff += "<input type='url'"
      elif varData['type']=='Text':
        buff += "<textarea "
      elif varData['type']=='Date' or varData['type']=='DateTime':
        if varData['showCalendar']:
          buff += "<input type='text' class='datepicker' data-config='" + json.dumps({
            "dateFormat": varData['formatEquivalent']
          }) + "'"
        else: 
          buff += "<input type='text'"
      else:
        buff += "<input type='text'"

      # There is a max_len limit
      if 'max_len' in varData:
        buff += " maxlength={max_len}".format(**varData)

      # Add the name to the field
      # The field with is configured with the class w-md-*
      # The possibles values are
      # - w-md-5
      # - w-md-10
      # - ....
      # - w-md-100
      
      # Remove the form-control or the checkboxes/radio are too big
      if varData['type']=='Bool':
        buff += " name='{name}' class=''".format(name = varData['name'])
      else:  
        buff += " name='{name}' class='form-control'".format(name = varData['name'])
        
      # Do we have a def value?
      if 'value' in varData:
        buff += ' value="{value}"'.format(**varData) 

      # ==== Now add all the validation attributes
      # if 'required' in varData and varData['required']:
      # Do not add the required attribute, otherwise it will be browser specific
      # how this element is marked. For example in Firefox only the required <select>
      # are marked with a red border, but the required <input> are not marked, so it
      # is confusing
      # buff += ' ' + attrRequired
      if varData['type']=='Word':
        buff += ' pattern="[A-Za-z0-9_]*"'

      # Do we have to hash this value?
      if 'doHash' in varData and varData['doHash']:
        buff += ' data-doHash="true"'

      # ... Finally, close the field definition. In some cases, we have to add 
      # some aditional stuff

      # select : add all the option
      if 'values' in varData:
        buff += ">\n"
        for value in varData['values']:
          i18nLabel=self.i18n(self.moduleName + ':' + varData['name'] + '_' + value)
          buff += "<option value='{value}' class='_i18n'>{i18nLabel}</option>\n".format(**locals()) 
        buff += "</select>\n"
      # FK : script for loading the data and create the <option> elements (if 
      # chooseFromList==False NOT add this)
      # If the element is hide DO NOT generate the select (see above)
      elif varData['type']=='FK' and (not 'chooseFromList' in varData or varData['chooseFromList']) and not varData['hide']:
        buff += "></select>\n"

        # Add the JS in order to fill the <select> 
        buff += self._getJS4Select(eId, varData)
      elif varData['type']=='Text':
        buff += "></textarea>\n"
      elif varData['type']=='File' or varData['type']=='Image':
        buff += """/>
          <div class="input-file-name"><span class="input-file-name"></span></div>
          <div class="input-file-btn btn btn-secondary" role="button">Examinar</div>
        </div>"""
      # Other : just close
      else:
        buff += "/>\n"

    # END : Block surround the input
    # In the new SOOCSS there is no such block!
    # if varData['type']!='Object':
    #   buff += "</div>"

    # END : Repeated Field
    if isRepeatedField:
      buff += "</div>\n"

    # END: Composed Field
    if varData['type']=='Object':
      buff += "</div>\n"
    # END : Regular field
    else:
      buff += """
        </div>
        <!-- /form-group -->
      </div>
      <!-- /regular-field -->"""

    return buff

  # -------------------------------------------
  # views/_{ActionName}{MODULE}.php.view.tmpl
  # View item's detail 
  # -------------------------------------------
    # For a list of field, generate all the input elements
  def _genViewEle4ListFields(self, fields, indCol=None):
    buff=""
    for varData in fields:
      if not indCol or int(varData['indCol'])==int(indCol):
        buff += self._genViewEle4OneField(varData)

    return buff

  # Similar to _genInputForm4OneField, generates all the HTML for viewing the 
  # fields taking into account the filed type
  #
  # Example:
  # <li class="w-md-20">
  #   <p class="fwb mvn fsm">Product name</p>
  #   <p class="fsm ">Air Chair</p>
  #  </li>
  def _genViewEle4OneField(self, varData):
    buff=""

    moduleName=self.moduleName
    name=varData['name']
    type=varData['type']

    # If this fields allows repetition, we have to create a _template 
    # to handle it
    isRepeatedField = 'repeat' in varData and varData['repeat']

    # Display?
    display = 'style="display:none;"' if 'hide' in varData and varData['hide'] else ' '
    
    # -------------------------------------------------------------------- Start

    # @TODO : Review in case of Objects with the newSOOCSS
    if varData['type']=='Object':
      buff += """
  <div class='{name}' {display}>""".format(**locals())
      # Group title
      buff += """
    <div>{name}</div>""".format(**locals())
    # Regular field
    else:
      buff += """
  <li class="{name}" {display}>""".format(**locals())
      # Field's label
      i18nFieldLabel = self.i18n("{moduleName}:{name}".format(**locals()))
      buff += """
    <p class="_i18n">{i18nFieldLabel}</p>""".format(**locals())

    # START : Repeated Field
    if isRepeatedField:
      buff += """
    <div class='_template'>"""

    # START : Block surround the input (in case a non Object)
    # Not in the new SOOCSS
    # if varData['type']!='Object':
    #   buff += """
    # <div class='col-sm-10'>"""

    # -------------------------------------------------------------------- Field
    
    # Object Field
    if varData['type']=='Object':
      buff += self._genViewEle4ListFields(varData['fields'])
    # Non Object field
    else:
      if type=='File':
        buff += """
      <a class="{name}URL" href="">{name}URL</a>""".format(**locals())
      elif type=='Image':
        buff += """
      <img class="{name}URL" href=""></img>""".format(**locals())
      elif varData['type']=='URL':
        buff += """
      <a class='{name}' href=''><span class='{name}'></span></a>""".format(**locals())
      elif type=='FK':
        fieldName=varData['fieldName']
        buff += """
      <p class="{name}{fieldName}"></p>""".format(**locals())
      elif varData['type']=='Bool':
        buff += "<input type='checkbox' disabled readonly value='1' class='{name} mls'/>".format(**varData)
      else:      
        buff += """
      <p class="{name}"></p>""".format(**locals())

    # ---------------------------------------------------------------------- End

    # END : Block surround the input
    # Not in the new SOOCSS
    # if varData['type']!='Object':
    #   buff += """
    # </div>"""

    # END : Repeated Field
    if isRepeatedField:
      buff += """
    </div>"""

    # END: Composed Field
    if varData['type']=='Object':
      buff += """
    </div>"""
    # END : Regular field
    else:
      buff += """
  </li>"""

    return buff

  def FormViewFieldsNoI18N(self, indCol):
    return self._genViewEle4ListFields(self.currentItemCfg['fields'], indCol)

  def HasViewCol(self, indCol):
    for fieldCfg in self.currentItemCfg['fields']:
      # print fieldCfg['indCol']
      if int(fieldCfg['indCol'])==int(indCol):
        return "OK"

    return ""
          
  # -------------------------------------------
  # views/_{ActionName}{MODULE}.php.list.tmpl
  # List of items
  # -------------------------------------------

  # {GUIListHeader}
  # The list header
  def printGUIListHeader(self):
    buff=""

    moduleName = self.moduleName
    for varData in self.currentItemCfg['fields']:
      if 'hide' in varData and varData['hide']: continue

      fieldName = varData['name']
      i18nFieldTitle = self.i18n("{moduleName}:{fieldName}".format(**locals()))

      buff += """
<th scope='col' class='{fieldName} _i18n'>{i18nFieldTitle}</th>""".format(**locals())

    return buff

  # {GUIListFilterFields}
  # Input fields just below the header for the user filter
  def GUIListFilterFields(self, idFilterForm):
    if not self.currentItemCfg or not 'listFilter' in self.currentItemCfg or not self.currentItemCfg['listFilter']:
      return ""

    moduleName=self.moduleName
    
    buff=""

    # @TODO : now listFilter is used, what happens if not defined od the fields are
    # different than the ones is 'fields'? This solution I do not like too much ...    
    listFields = self.currentItemCfg['fields'] 
    if 'listFilter' in self.currentItemCfg:
      listFields = self.currentItemCfg['listFilter'] 
      
    for varData in listFields:
      if 'hide' in varData and varData['hide']: continue

      fieldName=varData['name']

      i18nFieldLabel = self.i18n("{moduleName}:{fieldName}".format(**locals()))
      buff += """
      <div class="col-xs-12 col-sm-4 {fieldName}">
        <div class="form-group">
          <label class="control-label _i18n">{i18nFieldLabel}</label>""".format(**locals())
      
      # Dates, always filter by interval
      # @TODO : review this implementation, probably now is broken ...
      if varData['type']=='DateTime':
        formatEquivalent=varData['formatEquivalent']
        buff += """
            <input type='text' name='_start{fieldName}' class="datepicker form-control" data-type='date' data-format='{formatEquivalent}' /> - 
            <input type='text' name='_end{fieldName}'   class="datepicker form-control" data-type='date' data-format='{formatEquivalent}'/>""".format(**locals())
      elif varData['type']=='Date':
        formatEquivalent=varData['formatEquivalent']

        buff += "<div><input name='" + fieldName + "' type='text' class='datepicker' data-config='" + json.dumps({
          "dateFormat": varData['formatEquivalent']
        }) + "'/></div>"
      # Create an <select> with an empty <option>
      elif varData['type']=='FK':
        # @TODO : the <select/> could be selected using an expression WITHOUT and Id
        eId = self._getNewUniqueHTMLId() 
        buff += """
            <select id='{eId}' name='{fieldName}' class="form-control" /></select>""".format(**locals())
        # Add the JS
        buff += self._getJS4Select(eId, varData, False)
      # Boolean fields. In the filter this is NOT displayed as a checkbox but as a radio button (Yes/No/All)
      elif varData['type']=='Bool':
        i18nYes = self.i18n("FilterBoolYes")
        i18nNo  = self.i18n("FilterBoolNo")
        i18nAll = self.i18n("FilterBoolAll")
        
        buff += """
            <div>
              <input type='radio' name='{fieldName}' class='{fieldName}' value='1'/>
              <span class="_i18n">{i18nYes}</span>
              <input type='radio' name='{fieldName}' class='{fieldName}' value='0'/>
              <span class="_i18n">{i18nNo}</span>
              <input type='radio' name='{fieldName}' class='{fieldName}' checked/>
              <span class="_i18n">{i18nAll}</span>
            </div>""".format(**locals())
      else:  
        buff += """
            <input type='text' name='{fieldName}' class="form-control" /></input>""".format(**locals())

      buff += """
        </div>
      </div>"""

    return buff

  # {GUIListBodyTmpl}
  # The row where to put the list values  
  def printGUIListBodyTmpl(self):
    buff=""

    for varData in self.currentItemCfg['fields']:
      if 'hide' in varData and varData['hide']: continue

      if varData['type']=='File':
        buff += "<td><a class='{name}URL'>{name}URL</a></td>\n".format(**varData)
      elif varData['type']=='Image':
        buff += "<td><img class='{name}URL' width='50px'></img></td>\n".format(**varData)
      elif varData['type']=='URL':
        buff += "<td><a class='{name}' href=''><span class='{name}'></span></a></td>\n".format(**varData)
      elif varData['type']=='FK':
        buff += "<td class='{name}{fieldName}'></td>\n".format(**varData)
      elif varData['type']=='Bool':
        buff += "<td><input type='checkbox' disabled readonly value='1' class='{name}'/></td>\n".format(**varData)
      else:
        buff += "<td class='{name}'></td>\n".format(**varData)
    
    return buff

  # {ActionParamsObject}
  # Return an object with the 'params' defined in the JSON and the values 
  # provided in 'data'
  def ActionParamsObject(self,dataVarName, mode='useRuntimeValuesIfPresent'):
    if mode!='useRuntimeValuesIfPresent' and mode!='ignoreRuntimeValuesIfPresent':
      _raiseException('Allowed modes : useRuntimeValuesIfPresent and ignoreRuntimeValuesIfPresent')

    buff=""
    
    return "{}" if not 'params' in self.currentItemCfg else self._params2Array(self.currentItemCfg['params'], dataVarName, mode=='useRuntimeValuesIfPresent') 

  def printOrderByParams(self):
    if 'orderBy' in self.currentItemCfg:
      return json.dumps(self.currentItemCfg['orderBy'])
    else:
      return "[]"  

  # {OnClickAction}
  # Action performed when clicking on a certain item
  def printOnClickAction(self):
    # Go somewhere (over the rainbow)
    if 'onClick' in self.currentItemCfg and self.currentItemCfg['onClick']:
      onClickCfg=self.currentItemCfg['onClick']

      url = self._getActionUrl(onClickCfg['module'], onClickCfg['actionName'])
      # url=self.urlFE("/{module}/{actionName}{module}.html".format(**onClickCfg))
      params = '' if 'params' not in onClickCfg else self._buildQueryString(onClickCfg['params'],'data')
      # buff = "document.location = '{url}?' + {params}".format(**locals())
      return "'{url}?' + {params}".format(**locals())
    # No action performed when clicking
    else:
      # See {ActionName}{MODULE}.html.list.tmpl to understand why we do not return ""
      return "''"

  # {ListItemActions}
  def ListItemActions(self, varNameWithData, style):
    if 'itemActions' in self.currentItemCfg:
      # Only the actions with the style
      listActions=[]
      for actionCfg in self.currentItemCfg['itemActions']:
        if actionCfg['style']==style:
          listActions.append(actionCfg)

      return self._buildArrayActions(listActions, varNameWithData, False)
    else:
      return '[]'

  # If there are itemActions of a certain style
  def IsItemActions(self, style):
    tot = 0

    if 'itemActions' in self.currentItemCfg:
      tot = len(filter(lambda cfg: cfg['style']==style, self.currentItemCfg['itemActions']))
    
    return "true" if tot>0 else ""

  
  # {ListTotPerPage}
  # In the lists, number of records per page
  def printListTotPerPage(self):
    return str(self.currentItemCfg['totPerPage'])

  # Same number as in thead
  def printListTotCols(self):
    ncols=0

    # Item selector?
    ncols += 1 if len(self.IsItemActions('outrow'))>0 else 0

    # Visible cols
    for fieldCfg in self.currentItemCfg['fields']:
      if 'hide' not in fieldCfg or not fieldCfg['hide']:
        ncols += 1

    # Actions onrow
    ncols += 1 if len(self.IsItemActions('onrow'))>0 else 0

    return str(ncols)

  # -------------------------------------------
  # views/_{ActionName}{MODULE}.php.dashboard.tmpl
  # Dashboard : actions grouped in sections
  # -------------------------------------------
  def printDashboardSections(self):
    buff=""

    # Create Sections
    if 'sections' in self.currentItemCfg:
      thisModuleName=self.moduleName
      pageName=self.currentItemCfg['name']
      for sectionCfg in self.currentItemCfg['sections']:
        sectionName=sectionCfg['name']
        # I18N texts
        i18nSectionTitle = self.i18n("{thisModuleName}:{pageName}{sectionName}Title".format(**locals()))
        i18nSectionDesc  = self.i18n("{thisModuleName}:{pageName}{sectionName}Desc".format(**locals()))

        # Start Section
        buff += """
  <div class="panel panel-default">
    <div class="panel-heading">
      <h2 class="mvn _i18n">{i18nSectionTitle}</h2>
    </div>
    <div class="panel-body">
      <p class="fsm w-100 w-md-60 mbl _i18n">{i18nSectionDesc}</p>
      <div class="row">""".format(**locals())
        
        # Create Actions for every Section
        if 'actions' in sectionCfg:
          for actionCfg in sectionCfg['actions']:
            moduleName = actionCfg['module']
            actionName = actionCfg['name']
            # Lint to the action
            link = self._getActionUrl(moduleName, actionName)
            # link=self.urlFE('/{moduleName}/{actionName}{moduleName}.html'.format(**locals()))

            # I18N texts
            i18nActionTitle=self.i18n("{moduleName}:{actionName}:Title".format(**locals()))

            buff += """
        <div class="col-xs-12 col-sm-6 col-md-3">
          <div class="panel panel-demos">
            <div class="panel-heading pbn">
              <h3 class="panel-title mvn _i18n">{i18nActionTitle}</h3>
            </div>
            <div class="panel-footer">
              <a class="btn btn-default text-uppercase bg-primary w-100" href="{link}">
                Enter
              </a>
            </div>
          </div>
        </div>""".format(**locals())            

        # Close Section
        buff += """
      </div>
    </div>
  </div>"""

    return buff

  # -------------------------------------------
  # views/_{ActionName}{MODULE}.php.composed.tmpl
  # Composition of several other screens
  # -------------------------------------------
  def printComposedModules(self):
    buff=""

    # Create Sections
    if 'sections' in self.currentItemCfg:
      indSection=0
      for sectionCfg in self.currentItemCfg['sections']:
        # DO NOT USE directly + to concat strings (problems with unicode)
        # @TODO : sure there is a more "pythonic" way of doing the things! ;-)

        # OPEN SECTION 

        # --- Tab Panel
        if sectionCfg['style']=='tabPanel':
          buff="""
{buff}
<div>
  <ul class="nav nav-tabs ban mtl" role="tablist">""".format(**locals())
          
          # Create the tabs
          indAction=0
          for actionCfg in sectionCfg['actions']:
            classActive = "active" if indAction==0 else ""
            idTab = self.moduleName + '_' + self.currentItemCfg['name'] + '_' + str(indSection) + '_' + str(indAction)
            i18nTabTitle = self.i18n(actionCfg['label'])

            buff="""
    {buff}
    <li role="presentation" class="{classActive}">
      <a href="#{idTab}" aria-controls="home" role="tab" data-toggle="tab" class="_i18n">{i18nTabTitle}</a>
    </li>""".format(**locals())
            indAction += 1 
          
          buff="""
{buff}
  </ul>
  <div class="tab-content">""".format(**locals())
        # --- Flow
        else: 
          buff="""
{buff}
<div class="flex-container w-100 h-100">""".format(**locals())

        # Actions in sections      
        if 'actions' in sectionCfg:
          # Loop over all the actions that conform the composed page. Each action is
          # a reference to a module / action
          indAction=0
          for actionCfg in sectionCfg['actions']:
            # Search this module's configuration  
            moduleName=actionCfg['module']
            actionName=actionCfg['name']
            
            foundCfg = utils.search_dictionaries('name', actionName, self.allModulesConfig[moduleName]['actions'])
            if not foundCfg:
              raise Exception("Not found configuration for " + moduleName + 
                "." + actionName);
                # + " when generating composed page " + 
                #self.moduleName + "." + myItemCfg['name'])

            # Because we are change some things of foundCfg with the things  
            # that appear in actionCfg, we are going first to make a copy and
            # work on it to avoid possible side effects                      
            thisActionFullCfg = copy.deepcopy(foundCfg)

            # Ok, at this point let's clarify:                                  
            #                                                                   
            # actionCfg                                                         
            # ---------                                                         
            # Represents the "minimal" configuration for a moduleName:actionName
            # and it is the SMALL piece we have found in the composed           
            #                                                                   
            # foundCfg (and later thisActionFullCfg)                            
            # --------                                                          
            # represents the "original" configuration defined for this          
            # moduleName:actionName and it is the BIG piece containing all the  
            # default values and so one                                         

            # ----------------------- Actualize thisActionFullCfg with actionCfg

            # Params : because we are "calling" the action, that means in      
            # actionCfg (the composed) we MUST pass the values for those params
            if 'params' in thisActionFullCfg:
              # It is OBLIGATORY to define in actionCfg the action params
              # EXCEPT if thisActionFullCfg set default values for those params
              if 'params' not in actionCfg:                                       
                # TODO : we should perform a better check that only those params
                # that have a value in thisActionFullCfg are missing in actionCfg
                # BUT temporary we're just to remove this check
                actionCfg['params'] = [] 
                # composedModule = self.moduleName                                  
                # composedAction = self.currentItemCfg['name']                      
                # raise Exception("Error in {moduleName}.{actionName} : the original {composedModule}:{composedAction} has params but no values have been defined") 
              
              # Ok, now overwrite thisActionFullCfg['params'] with the info we
              # have set in actionCfg['params']
              utils.updateListMaps(thisActionFullCfg['params'], actionCfg['params'], 'name')
            
            # If we have specified a globalParams, overwrite the ones defined
            # by default (e.g. this is useful if we want to show less options 
            # for a widget when it is used in a composed)
            if 'globalActions' in actionCfg:
              thisActionFullCfg['globalActions'] = actionCfg['globalActions']

            # Update the collapsable/collapsed attribute
            thisActionFullCfg['collapsable'] = actionCfg['collapsable']
            thisActionFullCfg['collapsed'] = actionCfg['collapsed']

            # Set this config as current and generate
            # NOTE : here we have a problem with the custom code (only for the FE)
            # When we generate the code for a certain module the createWebModule
            # is called twice:
            # + First call : it receives as argument the folder 'templates/' => 
            #   that will find the file {ActionName}{MODULE}.html.composed.tmpl 
            #   => that contains {ComposedModules} => that will trigger this 
            #   portion of code
            # + Second call : it receives as argument the folder 'model/' =>
            #   some custom files are found and resolved
            #
            # The problem we have here is : how do we know which are those 
            # custom files? How can we resolve them with the 'thisActionFullCfg'
            #
            # The approach here (I know, it is not my best portion of code :-()
            # is to check if there is a customFile for the template we
            # are going to use and use the custom in fact that the template.
            # To do that we're going to "hardCode" some things but ....    


            # @TODO ; here we use ONLY the templates, no the default code ....
            # print "WARNING : when generating composed page using {module}.{name} actually custom code IS NOT USED!!!".format(**actionCfg)
            actionType = thisActionFullCfg['type']
            for tmpl in self.listTemplates[actionType]:
              # srcFile is something like 
              srcFile = tmpl['srcFile']
              dstFile = ResolverWebrad.getDstPath(self,tmpl['dstFile'])


              # Instantiate the resolver, so we do not have side effects with the 
              # current resolution
              # The Resolver is one like the current one (or subclass), only for
              # the FE side
              module = importlib.import_module(self.__class__.__name__)
              cResolver = getattr(module, self.__class__.__name__)
              resolver = cResolver(moduleName, self.allModulesConfig[moduleName], self.options)
              resolver.generateStartHTML = False
              resolver.generateEndHTML = False
              
              # Let's see if we are going to use the custom or the template
              # (read comment above)
              customFile = self._getCustomFile4Template(srcFile, actionCfg)
              if os.path.exists(customFile):
                newContent = resolver.genFileFromTmpl(customFile, None, thisActionFullCfg)
              else:
                newContent = resolver.genFileFromTmpl(srcFile, None, thisActionFullCfg)

              # How we're going to display the block depends on the style (tabPanel, flow,...)
              
              # ---- Tab Panel
              if sectionCfg['style']=='tabPanel':
                active = "active" if indAction==0 else ""
                idTab = self.moduleName + '_' + self.currentItemCfg['name'] + '_' + str(indSection) + '_' + str(indAction)

                buff="""
{buff}
<div role="tabpanel" class="tab-pane {active} panel pam bap" id="{idTab}">
  <div class="flex-container w-100">
    <div class="flex-item w-100">
      {newContent}
    </div>
  </div>
</div>""".format(**locals())
              # ---- Flow, un block after the other
              else:  
                # Each section is one block with width 100% and inside this block there 
                # are several blocks (each per acttion) with a width 100/# actions.
                # So the HTML for ONE section with 3 action has the form
                #  
                #   <div class="flex-container w-100 h-100">
                #     <div class="flex-item w-100 w-sm-33">
                #       HTML for Action 1
                #     </div>
                #     <div class="flex-item w-100 w-sm-33">
                #       HTML for action 2
                #     </div>
                #     <div class="flex-item w-100 w-sm-33">
                #       HTML for action 3
                #     </div>
                #   </div>        
                #
                # The class w-sm-XX, where XX = {100, 95, 90, ..., 5 } v { 33, 66 }
                numActions = len(sectionCfg['actions'])

                if sectionCfg['style']=='flow':
                  # It has no sense a block with more than 5
                  if numActions>5:
                    raise Exception("Are you sure you want a section with {numActions} actions??!!".format(**locals()))
                  if numActions==3:
                    actionWidth=33
                  else:
                    actionWidth=int(100/numActions)

                buff="""
{buff}
<div class="flex-item w-100 w-sm-{actionWidth}">
  {newContent}
</div>""".format(**locals())
     
            indAction += 1
        #!/end if actions

        # CLOSE SECTION (a serie of actions)

        if sectionCfg['style']=='tabPanel':
          buff="""
{buff}
  </div>
</div>""".format(**locals())
        else:  
          buff="""
{buff}
</div>""".format(**locals())
        
        indSection += 1
      #!end for sections
    
    # return all data    
    return buff

  # Ad-hocu tility used in printComposedModules to return the custom file for 
  # a certain template.
  # I know it is a ugly piece of code, but trying to solve in a more generic 
  # way using the existing code will imply a refractoring with a lot of side 
  # effects so .... 
  # @param tmplFile is /.../templates/Module/FE/SOOCSS/{ActionName}{MODULE}.html.view.tmpl
  def _getCustomFile4Template(self, tmplFile, cfgAction):
    # Get the file name, without ANY the folder and the 'tmpl extension'
    # This piece of code is from Resolver.getDstPath()
    # relPathWithExtension is something like
    # ./FE/SOOCSS/{ActionName}{MODULE}.html.add.tmp
    relPathWithExtension = os.path.basename(tmplFile)
    
    # relPath is something like
    # {ActionName}{MODULE}.html
    relPath = re.sub(r'\.\w+\.tmpl$', '', relPathWithExtension)

    # relPath will contain variables we have to replace using cfgAction.
    # The first approach could be use Resolver.resolveAllVars() but it depends 
    # that certain variables have been set previoulsy.... better take the portions
    # of code we need in our case

    # List of variables for that line
    listOfVars = set(re.compile(r"{\w+}").findall(relPath))
    # Transform, changing all the variables 
    for varName in listOfVars:
      value=None

      if varName=='{MODULE}':
        value=cfgAction['module']
      elif varName=='{ActionName}':
        value=cfgAction['name']

      if not value:
        raise Exception("Not know how to resolve the variable {varName} found in the file name {tmplFile}".format(**locals()))
      
      relPath = relPath.replace(varName, value)
    
    # We are close! Now, the "possible" (if any) custom file
    # code taken from printCustomHTML()
    prjHome=os.path.abspath(os.environ['PRJ_HOME']).replace("\\","/")
    moduleName=cfgAction['module']
    customFile  = \
      prjHome + \
      "/model/custom/ModuleCustom/FE/" + \
      os.environ['FE_TYPE'] + "/" + \
      moduleName + "/" + \
      relPath

    return customFile

  # -------------------------------------------
  # views/_{ActionName}{MODULE}.php.import.tmpl
  # -------------------------------------------
  def printActionParamsAsInputHidden(self):
    buff=""

    if 'params' in self.currentItemCfg:
      for paramCfg in self.currentItemCfg['params']:
        buff += """
        <input type="hidden" name="{name}"/> 
""".format(**paramCfg)

    return buff
