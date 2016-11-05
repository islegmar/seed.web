#!/usr/bin/python
# -------------------------------------------
# Resolver spedific for modules PHP
# @TODO: Do not overwrite not generate files (those that do not start with _)
# -------------------------------------------
import re
import os
import sys
import json
from ResolverModule import ResolverModule
from pprint import pprint

class ResolverModuleBEPHP(ResolverModule):

  def __init__(self, moduleName, cfgModule, options):
    ResolverModule.__init__(self, moduleName, cfgModule, options)

  def isBEResolver(self):
    return True

  def isFEResolver(self):
    return False

  # The conversors between the date format used in the JSON and PHP
  def getDateFormatEquivalences(self):
    return {
      'dd/MM/yy' : 'd/m/Y',
      'MM/dd/yy' : 'm/d/Y',
      'dd/MM/yy HH:mm' : 'd/m/Y H:i',
      'MM/dd/yy HH:mm' : 'm/d/Y H:i'
    }  

  # ============================================================================
  # 
  # Replacement Methods / No Templates
  # Reference to generic config as self.cfgModule['fields']
  #
  # ============================================================================

  # -------------------------------------------
  # General
  # -------------------------------------------
  
  # $VersionResolver
  def printVersionResolver(self):
    return "1.0" 

  # -------------------------------------------
  # onegocio/_{MODULE}.php
  # Bean onegocio
  # -------------------------------------------

  # {FieldDecl}      
  # Generates the fields' declarations as:
  #   protected $IdCliente = null;
  # See .tmpl to see why the fields are not declared as private 
  def printFieldDecl(self):
    buff=""
    for varData in self.cfgModule['fields']:
      # Set a default value
      if 'default' in varData:
        if varData['type']=='Integer':
          buff += """
    protected ${name} = {default}; // {type}""".format(**varData)
        else:
          buff += """
    protected ${name} = "{default}"; // {type}""".format(**varData)
      # No default value set
      else:  
        if varData['type']=='Bool':
          buff += """
    protected ${name} = 0; // {type}""".format(**varData)
        else:  
          buff += """
    protected ${name} = null; // {type}""".format(**varData)
  
    return buff
  
  # {GettersSetters}
  # Generates the Setters & Getters methods as:
  #   public void setName(Set name)....
  #   public String getName() ...
  # TODO
  # if ( !is_null(${name} ) && is_string(${name}) && strlen(${name}) > {max_len} ) {
  #   ${name} = substr(${name}, 0, {max_len});
  # }
  def printGettersSetters(self):
    buff=""
    for varData in self.cfgModule['fields']:
      line = """
  public function set{name}(${name}) {{
"""
      # -----------------------------
      # ---- Regular setter/getter
      # -----------------------------
      # If is Object, we have to store always an object
      if varData['type']=='Object':
        line += """
          $this->{name} = is_string(${name}) ? json_decode(${name}) : ${name};
"""   
      elif varData['type']=='Bool':
        line += """    
    $this->{name} = intval(${name})===1 ? 1 : 0;
"""
      else:
        line += """    
    $this->{name} = ${name};
"""
      line += """
  }}

  public function get{name}() {{
    return $this->{name};
  }}
"""
      # ---------------------
      # ---- Utility methods
      # ---------------------

      # *** File of Images
      if varData['type']=='File' or varData['type']=='Image':
        line += """
  // Utility : return the file pointed by as String
  public function get{name}AsString() {{
    return FactoryObject::newObject('_File')->loadById($this->get{name}())->getAsString();
  }}
""" 

      # *** Date
      if varData['type']=='FK':
        line += """
  // Utility : return the Object '{module}' pointed by the field {name}
  // @retun object od type {module}
  public function get{name}As{module}() {{
    return FactoryObject::newObject('{module}')->loadById($this->get{name}());
  }}
""" 

      # *** Date
      if varData['type']=='Date' or varData['type']=='DateTime':
        line += """
  // Utility : return the value of {name} as String
  public function get{name}AsString() {{
    return is_null($this->{name}) ? null  : date('{formatEquivalent}',$this->{name});
  }}"""
        # In the case of Date we do NOT receive HH:mm:ss BUT we must store with 
        # this precission, otherwise it will not possible yo have a good procession
        if varData['type']=='Date':
          line += """
  // Utility : receives the value of {name} as String using the format {formatEquivalent}
  // and connter it to an int
  public function set{name}AsString($dateAsString) {{
    if ( empty($dateAsString) ) {{
      $this->{name} = null;
    }} else {{
      $dtime = DateTime::createFromFormat('{formatEquivalent}' . ' H:i:s', $dateAsString . ' {time}');
      $this->{name} = $dtime->getTimestamp();    
    }}
  }}
"""
        else:  
          line += """
  // Utility : receives the value of {name} as String using the format {formatEquivalent}
  // and connter it to an int
  public function set{name}AsString($dateAsString) {{
    if ( is_null($dateAsString) ) {{
      $this->{name} = null;
    }} else {{
      $dtime = DateTime::createFromFormat("{formatEquivalent}", $dateAsString);
      $this->{name} = $dtime->getTimestamp();    
    }}
  }}
"""

      buff += line.format(**varData)
  
    return buff
  
  # {GetAsArray}
  # Given the object we weant to get an arry (if fact an object) representation
  # For every field we set
  #   $data[<FieldName>] = $this->get<FieldName>();
  # so at the end we get something like;
  #  { "Id" : 12, "Name": "Pepe" }
  def printGetAsArray(self):
    line=""
    for varData in self.cfgModule['fields']:
      # Note : If case field Object, the getXXX() will return always an object
      line += """
    $data['{name}'] = $this->get{name}();""".format(**varData)

    return line

  # {FillBeanFromArray}
  # Entries in the the method 
  #   fillBeanFromArray($data,$emptyAsNull=true,$prefix='')
  # This method is called when fex. we get get an object data's
  # representation in form of array (object?) fex. from a query 
  # or when submitting a form. 
  # For every value we have to call the corresponding set
  def printFillBeanFromArray(self):
    line=""
    for varData in self.cfgModule['fields']:
      line += """
    if ( isset($data[$prefix . '{name}']) ) {{
      $value = $data[$prefix . '{name}'];
      if ( $emptyAsNull && is_string($value) && strlen($value)==0 ) {{
        $value = null;
      }}
      $this->set{name}($value);
    }}  
""".format(**varData)
   
    return line
  
  # {AllFieldNamesCommaSeparated}
  # Return all the field names comma separated. This is used in:
  # + mod      : in the SELECT statement to select the element to update 
  # + load     : in the SELECT statement to select the element that is returned 
  # + list     : in the SELECT statement to select the elements returned
  # + onegocio : in the INSERT statement  
  # In case of SELECT we can have ambigueties mainly in the custom code if we
  # select several tables sharing the same field names, so this function can 
  # receive as argument the prefix 
  def AllFieldNamesCommaSeparated(self, fieldPrefix=None):
    line=""
    
    # @TODO : review this : 
    fieldsCfg = self.cfgModule['fields'] if not self.currentItemCfg else self.currentItemCfg['fields']

    for varData in fieldsCfg:
      # Skip transient/temporal fields
      if 'transient' in varData and varData['transient'] or 'temporal' in varData and varData['temporal']: 
        continue

      fieldName=varData['name']
      sep="," if len(line)>0 else ""

      if fieldPrefix:
        line += "{sep}{fieldPrefix}.{fieldName}".format(**locals())
      else:
        line += "{sep}{fieldName}".format(**locals())
  
    return line

  # {AllFieldNamesCommaSeparatedAsPlaceholders}
  # Return all the field names comma separated with : before, used for the 
  # INSERT (value section)
  def printAllFieldNamesCommaSeparatedAsPlaceholders(self):
    line=""
    for varData in self.cfgModule['fields']:
      # Skip transient fields
      if varData['transient']:
        continue

      if len(line)>0:
        line += ","
      line += ":{name}".format(**varData)
  
    return line

  # {SQLBindParams}
  # Return all the bindings, used to set the values when INSERT and UPDATE
  def printSQLBindParams(self):
    line=""
    for varData in self.cfgModule['fields']:
      # Skip transient fields
      if varData['transient']:
        continue

      # The thing with tmp is to avoid a warning of
      # "Only variables should be passed by reference"
      if varData['type']=='Object' or 'repeat' in varData and varData['repeat']:
        line += """
    $_{name} = json_encode($this->get{name}()); 
    $stmt->bindParam(':{name}', $_{name});\n
""".format(**varData)
      else:
        line += """
    $_{name} = $this->get{name}(); 
    $stmt->bindParam(':{name}', $_{name});\n
""".format(**varData)
  
    return line

  # {SQLAssign}
  # Return all the asignment for the UPDATE
  def printSQLAssign(self):
    line=""
    for varData in self.cfgModule['fields']:
      # Skip transient fields
      if varData['transient']:
        continue

      if len(line)>0:
        line += ","
      line += "{name} = :{name}".format(**varData)
  
    return line
 
  # -------------------------------------------
  # service/_Import{MODULE}.php
  # Bean onegocio
  # -------------------------------------------
  def printTransformers(self):
    if 'transformer' in self.currentItemCfg:
      return json.dumps(self.currentItemCfg['transformer']) 
    else:
      return '' 

  def printFieldTransformers(self):
    buff=""
    if 'transformer' in self.currentItemCfg:
      for fieldCfg in self.currentItemCfg['transformer']['fields']:
        if len(buff)>0:
          buff+=","   

        # Build 'config' (or leave it empty)
        # @TODO : only one level or params is allowed!!!!!
        config=""
        if 'config' in fieldCfg:
          for key in fieldCfg['config']:
            if len(config)>0:
              config += ","
            config += """
              '{key}' => '{val}'
""".format(key=key, val=fieldCfg['config'][key])  

        # Build 'indexes' (or leave it empty)
        # @TODO : only one level or params is allowed!!!!!
        indexes=""
        if 'indexes' in fieldCfg:
          for indexCfg in fieldCfg['indexes']:
            if len(indexes)>0:
              indexes += ","
            indexes += """
              array( 'index' => {index} )
""".format(**indexCfg)

        # This transformer config
        buff += """
          array (
            'name' => '{name}',
            'transformer' => '{transformer}',
            'indexes' => array(
              {indexes}
            ),
            'config' => array (
              {config}
            )
          )
 """.format(name=fieldCfg['name'], transformer=fieldCfg['transformer'], config=config, indexes=indexes)
    # Default importer (all fields imported as String)  
    else:
      for fieldCfg in self.cfgModule['fields']:
        if len(buff)>0:
          buff+=","   
        buff += """
          array (
            'name' => '{name}',
            'transformer' => 'TransformString'
          )
 """.format(**fieldCfg)

    return buff

  # ============================================================================
  # 
  # Replacement Methods / Templates
  # Reference self.currentItemCfg
  #
  # ============================================================================

  # -------------------------------------------
  # Generic
  # -------------------------------------------

  # -------------------------------------------
  # service/_{ActionName}{MODULE}Srv.php.<type>.tmpl
  # The services for the add/mod/other
  # -------------------------------------------

  # {BeanValidations}
  # In the add/mod, all the data's validations needed before perform the action
  # in the database  
  def BeanValidations(self,varNameObj, varNameBeanValidate):
    buff=""

    moduleName=self.moduleName
    for varData in self.currentItemCfg['fields']:
      name=varData['name']

      # Not validate the value if field is readOnly 
      if not varData['readOnly']:
        # The error message for i18n
        i18nErrorPrefix="{moduleName}:{name}Error".format(**locals())

        if 'required' in varData and varData['required']:
          i18nError=self.i18n(i18nErrorPrefix + 'Required')
          buff += """
    {varNameBeanValidate}->validateNonEmpty('{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())
          self.i18n(i18nErrorPrefix + 'Required')

        if varData['type']=='Word':
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotWord')
          buff += """
    {varNameBeanValidate}->validateIsWord('{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())
        
        if varData['type']=='NifNieCif':
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotNifNieCif')
          buff += """
    {varNameBeanValidate}->validateIsNifNieCif('{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())
        
        if varData['type']=='Email':
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotEmail')
          buff += """
    {varNameBeanValidate}->validateIsEmail('{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())

        if varData['type']=='Integer':
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotInteger')
          buff += """
    {varNameBeanValidate}->validateIsInteger('{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())
          # Validate min value
          if 'min_val' in varData:
            min_val=varData['min_val']
            i18nError=self.i18n(i18nErrorPrefix + 'IsIntegerTooSmall')
            buff += """
    {varNameBeanValidate}->validateIsIntegerNotTooSmall('{name}', $this->getParamValue('{name}',null), {min_val}, "{i18nError}");""".format(**locals())

          # Validate max value
          if 'max_val' in varData:
            max_val=varData['max_val']
            i18nError=self.i18n(i18nErrorPrefix + 'IsIntegerTooBig')
            buff += """
    {varNameBeanValidate}->validateIsIntegerNotTooBig('{name}', $this->getParamValue('{name}',null), {max_val}, "{i18nError}");""".format(**locals())
        
        if 'unique' in varData and varData['unique']:
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotUnique')
          buff += """
    {varNameBeanValidate}->validateIsUnique({varNameObj}, '{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())

        if varData['type']=='URL':
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotURL')
          buff += """
    {varNameBeanValidate}->validateIsURL('{name}', $this->getParamValue('{name}',null), "{i18nError}");""".format(**locals())

        if varData['type']=='Date':
          i18nError=self.i18n(i18nErrorPrefix + 'IsNotDate')
          formatDate = varData['formatEquivalent']

          buff += """
    {varNameBeanValidate}->validateIsDate('{name}', $this->getParamValue('{name}',null), "{formatDate}", "{i18nError}");""".format(**locals())

        # Validate max_len in all cases (String, Text,....). In some cases it has no sense (for example if Bool) but this
        # is just a configuration problem that should NOT be checked here
        if 'max_len' in varData:
          max_len=varData['max_len']
          i18nError=self.i18n(i18nErrorPrefix + 'TooLong')
          buff += """
    {varNameBeanValidate}->validateIsStringNotTooLong('{name}', $this->getParamValue('{name}',null), {max_len}, "{i18nError}");""".format(**locals())
    return buff

  # {OnlyOwnerCanModify}
  # Security check, this mod action can be only done by the data's owner
  def printOnlyOwnerCanModify(self):
    if 'onlyOwnerCanModify' in self.currentItemCfg and self.currentItemCfg['onlyOwnerCanModify']:
      return "true"
    else:
      return "false"

  # {FillBean}
  # Fill the bean ONLY with the fields specified in the action
  def FillBean(self, varNameObj):
    buff=""
    for varData in self.currentItemCfg['fields']:
      fieldType=varData['type']
      
      # Not set the value if field is readOnly  or temporal BUT we have not set the value
      if 'value' not in varData and (varData['readOnly'] or ('temporal' in varData and varData['temporal'])):
        pass
      # Otherwise, set the value 
      else:
        fieldName=varData['name']

        # If we have specified 'value' in the JSON that means we are NOT going to 
        # send this value from the FE but we set this value directly in the BE
        # (to avoid the FE sends a value different from the one we have spedified
        # in the JSON)
        if 'value' in varData:
          # Set null value      
          if varData['value']=='null':
            buff += """
    {varNameObj}->set{fieldName}(null);""".format(**locals())
          # Set a harcoded value
          else:
  
            # If the field is a FK, the value we have set is NOT the value (the Id)
            # BUT a value (code,...) can be used to get the Id from the related
            # object
            if fieldType=="FK":
              fieldValue="FactoryObject::newObject('{module}')->loadByField('{fieldName}', '{value}')->getId()".format(**varData)
            # For the string-like values, quote it
            elif fieldType=="String" or fieldType=="Word" or fieldType=="Password" or fieldType=="Email" or fieldType=="URL" or fieldType=="Text" or fieldType=="NifNieCif":
              fieldValue='"' + varData['value'] + '"'
            # Do not quote the value 
            else:
              fieldValue=varData['value']

            buff += """
    {varNameObj}->set{fieldName}({fieldValue});""".format(**locals())
        # We will receive the value from the request
        else:
          if fieldType=='Date' or fieldType=='DateTime':
            buff += """
    {varNameObj}->set{fieldName}AsString($this->getParamValue('{fieldName}',null));""".format(**locals())
          else:  
            buff += """
    {varNameObj}->set{fieldName}($this->getParamValue('{fieldName}',null));""".format(**locals())
    
    return buff  

  # {ParamsAsString4Log}
  # Return for the logger a String with all the params info  
  def printParamsAsString4Log(self):
    if 'params' in self.currentItemCfg:
      buff=""
      for paramCfg in  self.currentItemCfg['params']:
        if len(buff)>0: buff += " . ',' . "
        buff +=  "'{name}=' . $this->getParamValue('{name}','<not set>')".format(**paramCfg)
      
      return buff;
    else:
      return '""';  
    
  # -------------------------------------------
  # dao/_{ActionName}{MODULE}.php.list.tmpl
  # Service returning a data list. This output will be 
  # used by ListaPaginable ir order to generate the pagged lists
  # -------------------------------------------

  # {DaoListCompletarRow}
  # In completarData, add derived data using data extracted from the database.
  # Fex. in database we have an Id from a FK but we want to show the Name
  def printDaoListCompletarRow(self):
    buff=""
    
    # Becasue we are going to return this data to the client, we have to 
    # "sanitize" the values; we are not going to do it for ALL of them because
    # could introduce some errors (like Images where an URL is returned)

    for varData in self.currentItemCfg['fields']:
      varType = varData['type'] 
      # If one of the fields is a FK, that means we get the data doing a query
      # @TODO : It is not very effective, just for demo porpouses 
      if varType=='FK':
        # Only if 'module' is configured
        # We add a NEW field with (usuarlly) de FK's decription.
        # Fex. if we have FK : IdStatus and IdStatus=1 we will return
        # - IdStatus : 1
        # - IdStatusName : ACTIVE
        if 'module' in varData:
          buff += """
      if ( !is_null($row['{name}']) ) {{
        $row['{name}{fieldName}']=FactoryObject::newObject('{module}')->load($row['{name}'])->get{fieldName}();
      }} else {{
        $row['{name}{fieldName}']='';
      }}""".format(**dict(**varData))
      elif varType=='Date' or varType=='DateTime':
        buff += """
      $row['{name}']=is_null($row['{name}']) ? '' : date('{formatEquivalent}',$row['{name}']);""".format(**varData)
      elif varType=='File' or varType=='Image':
        buff += """
      $row['{name}URL']=is_null($row['{name}']) ? '' : '../../be/action/GetFileDB?Id=' . $row['{name}'] . '&fileName={name}-' . $row['{name}'];""".format(**varData)

    return buff

  # ------------------------------------------------------- Filter : param names
  # We build the query adding 'AND' conditions using several fields
  # _List{ActionName}{MODULE}.php.tmpl, getQuery() for more info

  # {SQLParamNames4PaggedList}
  # Add AND conditions to the WHERE clause corresponding to 'params', that
  # is the STATIC filter defined in the JSON 
  def printSQLParamNames4PaggedList(self):
    # No filter to apply
    if not self.currentItemCfg or not 'params' in self.currentItemCfg:
      return ""

    line=""
    for varData in self.currentItemCfg['params']:
      # Special case : null values. We must set the value here instead of 
      # SQLParamValues4PaggedList 
      if 'value' in varData and varData['value']=='null':
        line += " AND {name} IS NULL".format(**varData)
      # We have defined an operator                                
      elif 'operator' in varData:                                  
        line += " AND {name} {operator} :{name}".format(**varData) 
      # Default case                                               
      else:                                                        
        line += " AND {name} = :{name}".format(**varData)          

    return line

  # {SQLFilterNames4PaggedList}
  # Add AND conitions to the WHERE clause corresponding to 'listFilter', 
  # that is the DYNAMIC filter applied by the user. We will add it dynamically
  # to the query ONLY if we have received a value 
  # See _List{ActionName}{MODULE}.php.tmpl for more info
  def printSQLFilterNames4PaggedList(self):
    # No filter to apply
    if not self.currentItemCfg or not 'listFilter' in self.currentItemCfg or not self.currentItemCfg['listFilter']:
      return ""

    moduleName = self.moduleName
    line=""
    for varData in self.currentItemCfg['listFilter']:
      name = varData['name']
      operator = varData['operator']

      # Only add this field in the query if we have received the param
      # In order to avoid conflics with the field names, mainly when using
      # custom code and there are join on several tables with the same field
      # names, we prefix the field name with the table
      line += """
      if ( array_key_exists('{name}',$this->filterValues) ) $sql .= ' AND {moduleName}.{name} {operator} :{name}';""".format(**locals())
 
    return line

  # ------------------------------------------------------ Filter : param values
  # We return the parms' values we have added to the list query in the 
  # previous methods
  # _List{ActionName}{MODULE}.php.tmpl, getData4PreparedStmt() for more info
 

  # {SQLParamValues4PaggedList}
  # Return the values coming from the fields added coming from 'params'.
  def printSQLParamValues4PaggedList(self):
    # No filter to apply
    if not self.currentItemCfg or not 'params' in self.currentItemCfg:
      return ""

    line=""
    for varData in self.currentItemCfg['params']:
      # We have specified a hard-coded value in the JSON that is NOT null
      if 'value' in varData and varData['value']!='null':
        # Is a FK
        if varData['type']=='FK':
          line += """
      $data[':{name}'] = FactoryObject::newObject('{module}')->loadByField('{fieldName}','{value}')->getId();""".format(**varData)
        # Regular Value
        else:
          line += """
      $data[':{name}'] = '{value}';""".format(**varData)
      # The value comes specified in the request
      else:
        # In this case we do NOT have to distinguish the FK case, because it 
        # will come directly the value for the field (like IdSex=1)
        # BUT in the previous case, when we have specified a hardcoded value
        # in the JSON we can NOT put something like
        #  { "name" : "IdSex", "value" : "1" }
        # so to refer to that instance we want to use a business value like
        #  { "name" : "IdSex", "value" : "H" }
        # that will make the lookup and get the valuw with Id = 1
        line += """
      $data[':{name}'] = $this->filterValues['{name}'];""".format(**varData)
  
    return line

  # @TODO : unify with printSQLParamValues4PaggedList
  # This is a more generic function where we can specify the source and 
  # origin of the data
  # Return the values coming from the fields added coming from 'params'.
  def ParamValues4Query(self,nameOutputVar,nameInputFunc,nameInputVar=None):
    # No filter to apply
    if not self.currentItemCfg or not 'params' in self.currentItemCfg:
      return ""

    line=""
    for varData in self.currentItemCfg['params']:
      varName=varData['name']
      
      # We have specified a hard-coded value in the JSON that is NOT null
      if 'value' in varData and varData['value']!='null':
        varValue=varData['name']
        line += """
    {nameOutputVar}[':{varName}'] = '{varValue}';""".format(**locals())
      # The value comes specified in the request
      else:
        if nameInputVar:
          line += """
    {nameOutputVar}[':{varName}'] = {nameInputVar}['{varName}'];""".format(**locals())
        else:          
          line += """
    {nameOutputVar}[':{varName}'] = {nameInputFunc}('{varName}');""".format(**locals())
  
    return line

  # {SQLFilterValues4PaggedList}
  # Return the values coming from the fields added coming from 'listFilter'.
  def printSQLFilterValues4PaggedList(self):
    # No filter to apply
    if not self.currentItemCfg or not 'listFilter' in self.currentItemCfg or not self.currentItemCfg['listFilter']:
      return ""

    line=""
    for varData in self.currentItemCfg['listFilter']:
      # Only add this value if we have received the param
      line += """
      if ( array_key_exists('{name}',$this->filterValues) ) """.format(**varData)

      if varData['type']=='Date':
        line += """{{
        $dtime = DateTime::createFromFormat('{formatEquivalent}' . ' H:i:s', $this->filterValues['{name}'] . ' {time}');
        $data[':{name}'] = $dtime->getTimestamp();    
      }}""".format(**varData)
      else:
        if varData['operator']=='LIKE':
          line += "$data[':{name}'] = '%' . $this->filterValues['{name}'] . '%';".format(**varData)
        elif varData['operator']=='=':
          line += "$data[':{name}'] = $this->filterValues['{name}'];".format(**varData)
        else:
          raise Exception("[" + self.moduleName + ":" + self.currentItemCfg['name'] + "] Unknown compare operator " + varData['operator'])

    return line

  # {ListFieldNames}
  # List of fields returned by the list
  def printListFieldNames(self):
    buff=""

    for varData in self.currentItemCfg['fields']:
      if varData['type']!='transient':
        if len(buff)>0:
          buff += ","
        buff += varData['name']
    
    return buff

  # -------------------------------------------
  # service/_{ActionName}{MODULE}.php.chart.tmpl
  # Return info for chart
  # -------------------------------------------

  # {ActionSQL}
  def printActionSQL(self):
    if not 'sql' in self.currentItemCfg:
      raise Exception("No sql defined in action {name}".format(**self.currentItemCfg))

    return self.currentItemCfg['sql']
