<?php
require_once(dirname(__FILE__) . '/_ListAll_AuditLog.php');

/**
 * List of _AuditLog - custom code
 * 
 * In this case, we will check the hash are ok before showinf them
 * 
 * @author islegmar
 */
class ListAll_AuditLog extends _ListAll_AuditLog {
  // --------------------------------------------------------- _ListAll_AuditLog
  public function completarData(&$data, $db) {
    // Perform the default action 
    parent::completarData($data, $db);

    // Specific code : recompute the hash to be if it is ok
    foreach($data as &$row) {
      
      // This is the hash we have in the database
      $currHash = $row['Hash'];

      // Now compute the expected hash for this record
      $oAuditLog = FactoryObject::newObject('_AuditLog');
      $oAuditLog->loadById($row['Id']);
      $expectedHash = $oAuditLog->computeHash($db);

      $row['IsValid'] = $currHash===$expectedHash ? "OK" : "ERROR";
    }  
  }
}
?>
