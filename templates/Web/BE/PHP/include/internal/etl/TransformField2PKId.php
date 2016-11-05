<?php
require_once(INTERNAL_ROOT_DIR . '/etl/ITransform.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');

class TransformField2PKId implements ITransform {
  protected $bean;
  protected $fieldName;

	// ---------------------------------------------------------------- ITransform
	public function config($config) {
		$this->bean = FactoryObject::newObject($config->beanName);
	  $this->fieldName = $config->fieldName;
	}

  // $value represent the fieldName's value and we must return the Id
	public function transform($value) {
	  try {
		  $data = $this->bean->getByField($this->fieldName, $value);
		  
		  return $data['Id'];
	  } catch(NoRowSelectedException $e) {
	    return null;  	
	  }
  }
}
?>
