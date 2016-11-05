<?php
require_once(APP_ROOT_DIR . '/_MailServer/service/_DoActivate_MailServerSrv.php');

/**
 * Update a _MailServer - custom code
 */
class DoActivate_MailServerSrv extends _DoActivate_MailServerSrv {
  protected function checkSecurityImpl() {
    $id = $this->getParamValue('Id');

    $oMailServer = FactoryObject::newObject('_MailServer')->loadById($id);
  
    // Not activate if it is already active
    if ( $oMailServer->getActive() ) {
      throw new ActionDeniedException(); 
    }
  }

  public function updateInDatabase($oMailServer) {
    // Deactivate all the configurations
    $allMailServers = FactoryObject::newObject('_MailServer')->loadAll();
    foreach ($allMailServers as $ind => $tmp) {
      $tmp->setActive(0);
      $tmp->updateInDatabase();
    }

    parent::updateInDatabase($oMailServer);
  }  
}
?>
