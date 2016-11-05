<?php
require_once(APP_ROOT_DIR . '/_MailTemplate/service/_SendTestMail_MailTemplateSrv.php');

/**
 * Send a test mail using a certain _MailTenpolate and variables provided by the user
 *
 * @author islegmar@gmail.com
 */

class SendTestMail_MailTemplateSrv extends _SendTestMail_MailTemplateSrv {
  protected function performImpl() {
    $id = $this->getParamValue("Id");
    $email = $this->getParamValue("to");
    
    // jsonVars is tehr string representation of a JSON object and it will come
    // with &quote;
    // @TODO : not really working ....
    // $arrayVars = json_decode(stripcslashes($this->getParamValue("jsonVars","")));
    $arrayVars = array();

    FactoryObject::newObject("_MailTemplate")->loadById($id)->sendEmail(
      $email, 
      $arrayVars
    );

    return array();
  }
}
?>