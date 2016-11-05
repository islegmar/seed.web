<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebParams.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/controller/IAuthenticatedCtr.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');


/**
 * Base clase for all the controller. 
 * IMPORTANT : This classes DOES NOT receive the params in form of WebParams, 
 * every Controller is reponsable of getting the needed data from $_GET, $_POST,
 * $_FILES,.... This is because we have more freedom for accesing the data.
 * 
 * Also, this class does not handle any Exception. This is because some controllers
 * as the one that render a page will show an error page whils others as the services
 * just will return the error.
 * 
 * @author islegmar@gmail.com
 *
 */
abstract class Controller {
	protected $logger;
	protected $ppal;
	// IL - 05/11/13 - Get params only once
	private $params = null;
	
	public function __construct () {
		$this->logger = Logger::getLogger("main");
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('Created a instance of the controller "' . get_class($this) . '"');
		}
	}
	
	/**
	 * Utility : get WebParams if needed.
	 */
	protected function getWebParams() {
		if ( is_null($this->params) ) {
			$this->params = new WebParams();
		}
		
		return $this->params;
	}
	
	/**
	 * Executes the controller. It has access to all the request variables. 
	 * NOTE: 
	 * @return String or array()
	 */
	public function perform() {          
    $this->checkSecurity(WebSession::getInstance()->getPrincipal());
	}

  // IL - 25/01/15 
  // Check security for this controller
  // By default, ignore
  protected function checkSecurity($ppal) {
    if ( $this instanceof IAuthenticatedCtr ) {
      if ( $this->logger->isDebugEnabled() ) {
        $this->logger->debug('IAuthenticatedCtr. isAnonymous? ' . ($ppal->isAnonymous() ? "YES" : "NO"));
      }
      if ( $ppal->isAnonymous() ) {
        throw new Exception('Not user autenticated.');
      }
      // @TODO : do we use the ppal in Controller?
      $this->ppal = $ppal;
    }
  }
}
?>
