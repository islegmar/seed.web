<?php
require_once(APP_ROOT_DIR . '/_User/service/_ChangeMyPassword_UserSrv.php');

/**
 * Update a _User - custom code
 */
class ChangeMyPassword_UserSrv extends _ChangeMyPassword_UserSrv {
  // ------------------------------------------------- _ChangeMyPassword_UserSrv
  // This is a very specific case, because we do NOT receive an Id and to know
  // the data that is going to be changed, the current logged user will be used  
  protected function getObject2Update() {
    return FactoryObject::newObject('{MODULE}')->loadById(WebSession::getInstance()->getPrincipal()->getId());
  }

  /**
   * Check that:
   * + The pwd introduces twice matches
   */
  public function validateInputData($obj) {  
    parent::validateInputData($obj);

    $beanValidate = new ValidateBeanData();

    // ---- Check the new pwd introduced twice matches
    if ( strcmp($this->getParamValue('pwd1'), $this->getParamValue('pwd2'))!==0 ) {
      $beanValidate->addErrorCode('{i18n({MODULE}:pwd1ErrorNoMatchTwice)}', 'pwd1');
    }

    // Return the errors (if any)
    $errors = $beanValidate->getErrors(); 
    if ( !empty($errors) ) {
      throw new BeanValidateException($errors);
    }
  }

  /**
   * Set the new pwd
   */
  public function fillBean($oUser) {
    parent::fillBean($oUser);

    // Comppute the new pwd
    $credentialLoginPwd = FactoryObject::newObject('CredentialLoginPwd');
    $credentialLoginPwd->setLogin($oUser->getLogin());
    $credentialLoginPwd->setPwd($this->getParamValue('pwd1'));
    $newPwd = $credentialLoginPwd->getPwdPbkdf2();
    
    $oUser->setPassword($newPwd);
  } 
}
?>