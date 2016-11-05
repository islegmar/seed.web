<?php
require_once(dirname(__FILE__) . '/__MailServer.php');
require_once(EXTERNAL_ROOT_DIR . '/PHPMailer/PHPMailerAutoload.php');
//require 'PHPMailer/class.phpmailer.php';
//include("PHPMailer/class.smtp.php"); // optional, gets called from within class.phpmailer.php if not already loaded

/**
 * _MailServer - Custom code
 *
 * @author islegmar@gmail.com
 */
class _MailServer extends __MailServer {

    /**
     * Sends an email.
     * 
     * @TODO : this methods needs a deep refractoring
     */
    public function send($email,$strSubject,$strBody){

      if ( $this->getFake() ) {
        $this->logger->debug('[Send Mail] ====================================');
        $this->logger->debug('email : ' . $email);
        $this->logger->debug('subject : ' . $strSubject);
        $this->logger->debug('body : ' . $strBody);
        $this->logger->debug('================================================');
        
        return;
      }


      $mail = new PHPMailer();

      //$mail->SMTPDebug  = 2;                     // enables SMTP debug information (for testing)
      // 1 = errors and messages
      // 2 = messages only

      if ($this->getProtocol() == 'smtp'){

          $mail->SMTPOptions = array(
              'ssl' => array(
                  'verify_peer' => false,
                  'verify_peer_name' => false,
                  'allow_self_signed' => true
              )
          );

          $mail->IsSMTP(); // telling the class to use SMTP
      }

        //$body             = file_get_contents('contents.html');
        //$body             = eregi_replace("[\]",'',$body);


       $mail->Host       = $this->getHost();      // SMTP server
       $mail->SMTPAuth   = $this->getAuth();      // enable SMTP authentication
       $mail->SMTPSecure = $this->getSecure();    // sets the prefix to the servier
       $mail->Port       = $this->getPort();     // set the SMTP port for the GMAIL server
       
       if ( $mail->SMTPAuth ) {
         $mail->Username   = $this->getUsername(); // GMAIL username
         $mail->Password   = $this->getPassword(); // GMAIL password        
       // @TODO : Not sure about that.... 
       } else {
         $mail->SMTPAutoTLS = false;
       }

       $mail->SetFrom   ($this->getUsername(), 'mail');
       $mail->AddReplyTo($this->getUsername(),"mail");

       $mail->Subject    = $strSubject;

       $mail->AltBody    = "To view the message, please use an HTML compatible email viewer!"; // optional, comment out and test

       $mail->MsgHTML($strBody);

       //$mail->Body    = 'This is the HTML message body <b>in bold!</b>';

       $mail->AddAddress($email, "mail");

       //$mail->AddAttachment("images/phpmailer.gif");      // attachment
       //$mail->AddAttachment("images/phpmailer_mini.gif"); // attachment

       if(!$mail->Send()) {
           if ( $this->logger->isDebugEnabled() ) {
               $this->logger->debug("Mailer Error: " . $mail->ErrorInfo);
           }
       } else {
           if ( $this->logger->isDebugEnabled() ) {
               $this->logger->debug("Mail Sent!!!!!!!!!");
           }
       }

   }
}
?>
