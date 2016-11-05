<?php
require_once(APP_ROOT_DIR . '/_MailServer/service/_AddAll_MailServerSrv.php');

/**
 * Adds a _MailServer - custom code
 *
 * @author islegmar@gmail.com
 */

class AddAll_MailServerSrv extends _AddAll_MailServerSrv {

  public function validateInputData($obj) {
    parent::validateInputData($obj);
    $beanValidate = new ValidateBeanData();

    // Ensure that there is ONLY once MailServer active
    if($this->getParamValue("Active",null)){
      try{
        $activeMailServer = FactoryObject::newObject('_MailServer');
        $activeMailServer->loadByField("Active",true);

        if( $activeMailServer->getId()!==$this->getParamValue("Id",null)){
          $beanValidate->addErrorCode('{i18n({MODULE}:ActiveErrorAnotherMailServerIsActive)}', 'Active', array('$nameMailServer'),array($activeMailServer->getMID()));
        }
      } catch (NoRowSelectedException $e) {}
    }

    $errors = $beanValidate->getErrors();
    if ( !empty($errors) ) {
      throw new BeanValidateException($errors);
    }
  }
}
?>
