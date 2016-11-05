<?php
require_once(APP_ROOT_DIR . '/_ConfigApp/service/_DoActivate_ConfigAppSrv.php');

/**
 * Activate one of the ConfigApp
 */
class DoActivate_ConfigAppSrv extends _DoActivate_ConfigAppSrv {
  protected function checkSecurityImpl() {
    $id = $this->getParamValue('Id');

    $oConfigApp = FactoryObject::newObject('_ConfigApp')->loadById($id);
  
    // Not activate if it is already active
    if ( $oConfigApp->getIsActive() ) {
      throw new ActionDeniedException(); 
    }
  }

  public function updateInDatabase($oConfigApp) {
    // Deactivate all the configurations
    $allConfigApps = FactoryObject::newObject('_ConfigApp')->loadAll();
    foreach ($allConfigApps as $ind => $tmp) {
      $tmp->setIsActive(0);
      $tmp->updateInDatabase();
    }

    parent::updateInDatabase($oConfigApp);
  }  
}
?>
