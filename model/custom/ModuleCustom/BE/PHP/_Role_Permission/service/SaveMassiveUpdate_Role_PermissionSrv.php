<?php
require_once(APP_ROOT_DIR . '/_Role_Permission/service/_SaveMassiveUpdate_Role_PermissionSrv.php');

/**
 * Generic service for _Role_Permission - custom code
 *
 * @author islegmar@gmail.com
 */

class SaveMassiveUpdate_Role_PermissionSrv extends _SaveMassiveUpdate_Role_PermissionSrv {
  // ------------------------------------- _SaveMassiveUpdate_Role_PermissionSrv
  protected function performImpl() {
    //$matrix = $this->getParamValue('matrix');
    $matrix = $_POST['matrix'];

    // Delete all the _Role_Permission
    $oRolePermission = FactoryObject::newObject('_Role_Permission');
    $oRolePermission->deleteAll();

    // Recreate ONLY with the data we have received, corresponding to the 
    // combinatios that are active
    foreach ($matrix as $ind => $data) {
      $oRolePermission = FactoryObject::newObject('_Role_Permission');
      $oRolePermission->setId_Role($data['RoleId']);
      $oRolePermission->setId_Permission($data['PermissionId']);
      $oRolePermission->createInDatabase();
    }    
    
    return array();
  }
}
?>
