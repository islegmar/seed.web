<?php
require_once(APP_ROOT_DIR . '/_User/service/_PublicRegister_UserSrv.php');

/**
 * When the user is registered, an e-mail is sent
 *
 * @author islegmar@gmail.com
 */

class PublicRegister_UserSrv extends _PublicRegister_UserSrv {
  /**
   * Check that:
   * + The old pwd is ok
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
   * Create the user + send an activation e-mail
   */
  public function createInDatabase($oUser) {
    $oUser->register($this->getParamValue('pwd1'));
  } 
}
?>