<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');

/**
 * Base class to create mails
 * 
 * @author Isi 
 */
abstract class Mail  {
	protected $logger;
	private $to;
	private $from;

	public function Mail($logger) {
       $this->logger = $logger;
  }
    
  // ------------------------------------------------------------------- Setters  
	public function setTo($to) {
	   $this->to = $to;
	}
	
	public function setFrom($from) {
	   $this->from = $from;
	}

  // ---------------------------------------------------------- Métodos Públicos 
	public function send() {
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug('[Mail] mail(from:' . $this->from . ' to:' . $this->to . ')...');
    }
    $headers  = "MIME-Version: 1.0\r\n";
    $headers .= "Content-type: text/html; charset=iso-8859-1\r\n";
		$headers .= "From: $this->from\r\n";
		
    //options to send to cc+bcc 
    $subject = $this->getSubject();
    $content = $this->getContent();
        
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug('[Mail] mail(' . $this->to . ',' . $subject . ',' . $content . ')');
    }
    if ( !mail( $this->to, $subject, $content, $headers ) ) {
      throw new Exception("Error al enviar mail");            
    } 
  }
    
  private function sendMail() {
  }
    
  // ---------------------------------------------------------- Abstract Methods
  protected abstract function getContent();
  protected abstract function getSubject();    
}
?>
