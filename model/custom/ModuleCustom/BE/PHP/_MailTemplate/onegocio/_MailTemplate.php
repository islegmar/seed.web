<?php
require_once(dirname(__FILE__) . '/__MailTemplate.php');

/**
 * MailTemplate
 *
 * @author islegmar@gmail.com
 */
class _MailTemplate extends __MailTemplate {
  /**
   * Sends this MailTemplate to a certain email address, resolving all the 
   * placeholders in subject and content. The active _MAilServer is used.
   *
   * @param String $email the e-mail address 
   * @param Array $arrayVars Map with key values
   * @param Atray $type The template's identifier (field MID) 
   */
  public function sendEmail($email, $arrayVars) {
    // Resolve Subject
    $strSubject = $this->replacePlaceholders($this->getSubject(), $arrayVars);

    // Resolve Content
    $strBody = $this->replacePlaceholders($this->getContent(), $arrayVars);

    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug('subject "' . $strSubject . '", body "' . $strBody . '"');
    }

    // Send the amil using the active MailServer
    FactoryObject::newObject('_MailServer')->loadByField("Active",1)->send($email,$strSubject,$strBody);
  }

  // ------------------------------------------------------- Protected Functions
  /**
   * @param $arrayVars Array with pairs var/val
   * @return String Returns the input data with all the placeholders resolved
   */
  protected function replacePlaceholders($str, $arrayVars) {
    foreach ($arrayVars as $key => $value) {
      $str = str_replace($key, $value, $str);
    }

    return $str;
  }
}
?>