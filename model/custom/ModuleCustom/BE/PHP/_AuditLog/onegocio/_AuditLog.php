<?php
require_once(dirname(__FILE__) . '/__AuditLog.php');

/**
 * _AuditLog - custom code
 *
 * When inserting a hash is computed 
 *
 * @author islegmar@gmail.com
 */
class _AuditLog extends __AuditLog {
  // Compute the hash code for this record
  public function computeHash($db=null) {
    // Compute the hash taken into account the previous record and the data to be 
    // inserted
    // Get the hash from the LAST record (chain)
    $lastRecordHash='';
    try {
      $oLast = FactoryObject::newObject('_AuditLog');
      // Search the last one
      if ( is_null($this->getId()) ) {
        $oLast->findOneWithStmt('SELECT * FROM _AuditLog ORDER BY Id DESC LIMIT 1', null, true);
      // Search the previous one
      } else {
        $oLast->findOneWithStmt('SELECT * FROM _AuditLog WHERE Id<:Id ORDER BY Id DESC LIMIT 1', array(':Id' => $this->getId()) , true);        
      }
      $lastRecordHash=$oLast->getHash();
    } catch ( NoRowSelectedException $e) {
      // That means is the first record, so use empty value
    }

    return md5(
      $this->getId_User()  . '|' .
      $this->getModule()   . '|' .
      $this->getAction()   . '|' .
      $this->getTheDate()  . '|' .
      $lastRecordHash
    );
  }
  // ---------------------------------------------------------------- __AuditLog
  public function createInDatabase($db=null) {
    // Compute the hash and set the value
    $this->setHash($this->computeHash($db));

    // Now, create in database
    return parent::createInDatabase($db);
  }
}
?>
