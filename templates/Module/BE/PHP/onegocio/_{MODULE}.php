<?php
require_once(APP_ROOT_DIR . '/php/BaseOBean.php');

/**
 * _{MODULE}Bean
 */
class _{MODULE} extends BaseOBean {
  public $TABLE_NAME = '{MODULE}';

  {FieldDecl}
	
  // --------------------------------------------------------- Setters & Getters
  // NOTE : the fields are declared as protected and not as private to allow
  // the extended class to have access directly to the field in case we need 
  // for example to overwrite a getXXX() method
  {GettersSetters}


  // ------------------------------------------------------- Data Transformation
  function getAsArray($pData=null) {
    $data = parent::getAsArray($pData);
    {GetAsArray}

    return $data;
  }

  public function fillBeanFromArray($data,$emptyAsNull=true,$prefix='') {
    if ( isset($data['Id']) ) $this->setId($data['Id']);
    if ( isset($data['IdOwner']) ) $this->setIdOwner($data['IdOwner']);

    {FillBeanFromArray}  
  }

  // -------------------------------------------------------------- DB Functions
  public function deleteAll($pDb=null) {
    $db = !is_null($pDb) ? $pDb : DBConnectionManager::get();

    return $this->updateOrInsert('DELETE FROM ' . $this->TABLE_NAME,$db); 
  }

  public function createInDatabase($pDb=null) {
    $db = !is_null($pDb) ? $pDb : DBConnectionManager::get();

    $sql=<<<EOD
    INSERT INTO $this->TABLE_NAME (
      IdOwner,
      {AllFieldNamesCommaSeparated()}
    ) VALUES (
      :IdOwner,
      {AllFieldNamesCommaSeparatedAsPlaceholders}
    )   
EOD;

    $stmt = $db->getPDOConnection()->prepare($sql);
    $_IdOwner = $this->getIdOwner();
    $stmt->bindParam(':IdOwner', $_IdOwner);
    {SQLBindParams}
    $stmt->execute();
    $this->Id = $db->getInsertId();

    return $this->Id;
  }

  public function updateInDatabase($pDb=null) {
    $db = !is_null($pDb) ? $pDb : DBConnectionManager::get();

    $sql=<<<EOD
    UPDATE $this->TABLE_NAME SET
      IdOwner = :IdOwner,
      {SQLAssign}
    WHERE Id = $this->Id
EOD;
    $stmt = $db->getPDOConnection()->prepare($sql);
    $_IdOwner = $this->getIdOwner();
    $stmt->bindParam(':IdOwner', $_IdOwner);
    {SQLBindParams}
    $stmt->execute();
    
    return $db->getAffectedRows();
  }  

  public function deleteInDatabase($pDb=null) {
    $db = !is_null($pDb) ? $pDb : DBConnectionManager::get();

    $sql=<<<EOD
    DELETE FROM $this->TABLE_NAME 
    WHERE Id = :Id
EOD;
    $stmt = $db->getPDOConnection()->prepare($sql);
    $_Id = $this->getId();
    $stmt->bindParam(':Id', $_Id);
    $stmt->execute();
    
    return $db->getAffectedRows();
  }  
}
?>
