<?php
require_once(APP_ROOT_DIR . '/_User/service/_GetCurrent_UserSrv.php');

/**
 * Return the current user
 *
 * @author islegmar@gmail.com
 */

class GetCurrent_UserSrv extends _GetCurrent_UserSrv {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    $ppal = WebSession::getInstance()->getPrincipal();

    if ( $ppal->isAnonymous() ) {
      return array( 'permissions' => array());
    // Reload the user from the database just in case the data has changed
    } else {
      return FactoryObject::newObject('{MODULE}')->loadById($ppal->getId())->getAsArray();
    }
  }
}
?>