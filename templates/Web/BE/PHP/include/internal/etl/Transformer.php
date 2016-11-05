<?php

/*
 * Transform a entry (fex. a string read from a CSV fiLe) into a 
 * Map<String=FieldName,Object=Any transformed value>
 */
class Transformer {
  // Array of hardcoded values
  protected $hardcodedValues = array();

  // An array with the different transformers, already condifured.
  // [ 
  //   { 
  //     'name' : Field Name, 
  //     'indexes' : [ index,...], => OPTIONAL
  //     'transfomer' : object ITransformer already configured
  //     'value' : value (in case it does NOT come from the source data) ==> OPTIONAL
  //   },
  //   ...
  // ]
  protected $transformers;

  /**
   * Receives the config (as JSON)
   *
   * 'fields' : [
   *   {
	 *     'name' => The field name
	 *     'transformer' => The tranformer's bean name
   *     'indexes' : [ => OPTIONAL
   *       { 'index' : 1 }, ....
   *     ],
   *     'config : {
   *       => The transformer's configuration (depends on the transformer)
   *     },
   *     'value' : ... => OPTIONAL : If it is a hardcoded value obtained 
   *                      applying a transformer (typical case, the FK)
   *   }
   * ]
   */
  public function config($config) {
  	$this->transformers = array();
  	$fieldsCfg = $config->fields;
  	foreach ($fieldsCfg as $ind => $fieldCfg) {
      // A transformer has been defined  
      if ( array_key_exists("transformer", $fieldCfg) ) {
        // Instantitate the transformer
        $transformer = FactoryObject::newObject($fieldCfg->transformer);

        // Config the transformer (if defined)
        if ( array_key_exists('config', $fieldCfg)) {
          $transformer->config($fieldCfg->config);
        }

        // If we have defined 'values', that means this transformer is used
        // to obtain a STATIC value, not a dynamic one from the input data
        if ( array_key_exists("value", $fieldCfg) ) {
          // OK, now let's apply the transformer to values to obtain the 
          // harcoded value

          $newVal = $transformer->transform($fieldCfg->value);
          $this->hardcodedValues[$fieldCfg->name] = $newVal;
        // The usual way, we will transform the input data
        } elseif ( array_key_exists("indexes", $fieldCfg) ) {
          // Get the indexes we will use when getting the original value 
          $indexes = null;
          if ( array_key_exists('indexes', $fieldCfg) ) {
            $indexes = array();
            foreach ($fieldCfg->indexes as $indexCfg) {
              array_push($indexes, $indexCfg->index);
            }
          }

      		array_push($this->transformers, array(
            'name' => $fieldCfg->name,
            'indexes' => $indexes,
            'transformer' => $transformer
      		));
        } else {
          throw new Exception("No fields neither value defined for the transformer $fieldCfg->transformer");
        }
      // Hardcoded value  
      } else {
        if ( array_key_exists("value", $fieldCfg) ) {
          $this->hardcodedValues[$fieldCfg->name] = $fieldCfg->value;
        } else {
          throw new Exception("No transformer neither value defined!");
        }

      }
  	}
  }

  /**
   * Transform List<String> in a Map<String,Object>
   */
  public function /*Map<String,Object>*/ transform(/*List<String>*/ $data) {
  	$transformedData = array();

    // Execute all the transfomers on the original data
    foreach($this->transformers as $ind=>$transformerCfg) {
      $val = null;

      // Get the original value to be transformed. If indexes is defined use them,
      // otherwise use $ind
      if ( is_null($transformerCfg['indexes']) || count($transformerCfg['indexes'])==0 ) {
        $val = $data[$ind];
      } else {
        // Single value
        if ( count($transformerCfg['indexes'])==1 ) {
          $indArray = $transformerCfg['indexes'][0];
          $val = (array_key_exists($indArray, $data)  ? $data[$indArray] : null);
        // List of avalues
        } else {
          $val=array();
          foreach($transformerCfg['indexes'] as $index ) {
            array_push($val, array_key_exists($index, $data) ? $data[$index] : null);
          }    
        }
      }

      $fieldName = $transformerCfg['name'];
      $newVal = $transformerCfg['transformer']->transform($val);

      $transformedData[$fieldName] = $newVal;
    }

    // Finally, add the hardcoded values    
    return array_merge($transformedData, $this->hardcodedValues);    
  }
}
?>