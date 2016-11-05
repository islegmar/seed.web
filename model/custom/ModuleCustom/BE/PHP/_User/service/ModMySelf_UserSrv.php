<?php
require_once(APP_ROOT_DIR . '/_User/service/_ModMySelf_UserSrv.php');

/**
 * A user updates his own data. From here he can change everything EXCEPT 
 * the pwd.
 *
 * @author islegmar@gmail.com
 */

class ModMySelf_UserSrv extends _ModMySelf_UserSrv {
  // -------------------------------------------------------- _ModMySelf_UserSrv
  // This is a very specific case, because we do NOT receive an Id and to know
  // the data that is going to be changed, the current logged user will be used  
  protected function getObject2Update() {
    return FactoryObject::newObject('{MODULE}')->loadById(WebSession::getInstance()->getPrincipal()->getId());
  }
}
?>