<?php
require_once(APP_ROOT_DIR . '/_MailServer/service/_SendTestMail_MailServerSrv.php');

/**
 * Send a test mail using the active MailServer
 *
 * @author islegmar@gmail.com
 */

class SendTestMail_MailServerSrv extends _SendTestMail_MailServerSrv {
  protected function performImpl() {
    $email = $this->getParamValue("to");
    $subject = $this->getParamValue("subject");
    $content = $this->getParamValue("content");

    FactoryObject::newObject("_MailServer")->loadByField('Active',1)->send(
      $email,
      $subject,
      $content
    );

    return array();
  }
}
?>