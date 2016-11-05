<?php
require_once(APP_ROOT_DIR . '/_User/service/_AddAll_UserSrv.php');

/**
 * Add a _User
 *
 * @author islegmar@gmail.com
 */
class AddAll_UserSrv extends _AddAll_UserSrv {
  // Compute the password usign Pbkdf2
  public function fillBean($obj) {
    parent::fillBean($obj);

    $credentialLoginPwd = FactoryObject::newObject('CredentialLoginPwd');
    $credentialLoginPwd->setLogin($obj->getLogin());
    $credentialLoginPwd->setPwd($this->getParamValue('Password'));

    $obj->setPassword($credentialLoginPwd->getPwdPbkdf2());
  }
}
?>
