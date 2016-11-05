<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/utils/Params.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');

/**
 * Base clase for all the services. 
 *
 * Those services are independent of the protocol used (json, xml,...)
 * 
 * @author islegmar@gmail.com
 */
abstract class Service {
  // @todo : it's a bit chaos what params can be; until now it can be:
  // @TODODELAMUERTE : it's a bit chaos what params can be; until now it can be:
  // - instance of WebParam 
  // - a JSON object
  // - an array
  // This params is set by the controller
  // See Service2AjacController
	protected $params;
	protected $logger;

	public function __construct () {
		$this->logger = Logger::getLogger("main");
    
		$this->params = new Params(array());

		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('Created a instance of the service "' . get_class($this) . '"');
		}
	}
	
	/**
	 * Set the params for this service
	 *
	 * @param Params $params
	 * @retval Service This object (to allow chaining)  
	 */
  public function setParams ($params) {
		$this->params = $params;
		return $this;	
	}

	/**
	 * Add a new param value to this service.
	 *
	 * @param String $key The param name
	 * @param Object $value The param value
	 * @retval Service This object (to allow chaining)  
	 */
	public function addParam ($key, $value) {
		$this->params->setParam($key, $value);
		return $this;
	}
	
	/**
	 * Returns a param's value of a default value if not set.
	 *
	 * @note In order o indicate that the defaultValue is not set se use this special string
	 * instead null/false... because those could be valid values.
	 * @note See note above about the nature of params
	 *
	 * @param String $paramName Name of the parameter
	 * @param String $defaultValue Default value returned in case paramName is not found. 
	 * @throws Exception If paramName is NO found and NO default value is set  
	 */
	public function getParamValue($paramName, $defaultValue='__VALUE_NOT_SET__', $scapeHtml=true) {
		// Array. Not used
		if ( is_array($this->params ) ) {
			$val = isset($this->params[$paramName]) ? $this->params[$paramName] : $defaultValue;
		// Params. Actually only used for
    // _completeFK
    // Id
    // lang
    // setAsCurrLang
		} else if ( $this->params instanceof Params ) {
			$val = $this->params->getParam($paramName, $defaultValue);
		// JSON. This is the one used mainly when retrieving the data entered by 
		// the user in forms
		} else if ( is_object($this->params) ) {
			// @todo : I'm not sure if this is a good solution :-( We can still try to get
			// the parameter for the request (that is useful when htaccess add parameters to the call)
			$val = isset($this->params->{$paramName}) ? $this->params->{$paramName} : ( isset($_REQUEST[$paramName]) ? $_REQUEST[$paramName] : $defaultValue);
		
      // It has been decided to DO NOT sanitize the variables here neither 
      // in the database. They are ONLY sanitized in the FE and in the SQL 
      // because only prepared statements are used

			if ( !is_null($val) && is_string($val) ) {
				// OK, if it as empty value we will treat this as a null ...
				// This change comes form the following situation:
				// + A FK field rendered as a <select> with an empty option
				// + When the values are sent from the client, this field has the value ""
				// + In the server it is checked if it NOT NULL, so "" is ok
				// + When building the query fex. to insert, it fails
				// DO NOT USE empty()!!! It will return TRUE if fex. the value is 0 (as in 
				// a checkbox)
				if (strlen(trim($val))==0) {
					$val=null;
				} 
			}
		} else {
			throw new Exception('Params of type  "' . gettype($this->params) . '" not valid.');			
		}
		
		if ( $val==='__VALUE_NOT_SET__' ) {
			throw new Exception('Param "' . $paramName . '" not set and not default value provided');			
		}

		return $val;
	}
	
	/**
	 * Get all params as an array
	 *
	 * @retval array Array with paramName as key and paramValue as vañue
	 */
	public function getAllParamsAsArray() {
		// Array
		if ( is_array($this->params ) ) {
			return $this->params;
		// Params	
		} else if ( $this->params instanceof Params ) {
			return $this->params->getAllParams();
		// JSON	
		} else if ( is_object($this->params) ) {
			return (array)$this->params;
		} else {
			throw new Exception('Params of type  "' . gettype($this->params) . '" not valid.');			
		}
	}
	
	/**
	 * Returns the current Principal.
	 *
   * @retval IPrincipal The current principal (it can be an AnonymousUser or an
   * autehnticated one) 
	 */
	protected function getPrincipal() {
		$webSession = WebSession::getInstance();
		return $webSession->getPrincipal();
	}
	
	/**
	 * Perform the business actions and return the info as array
	 * NOTE : careful with the generic code is added here; at the moment only
	 * the check security is performed.
	 * 
	 * @retval array Array with all the data.
	 */
  final public function perform() {
    try {
      $this->checkSecurity();
    }
    catch (Exception $e) {
      $ppal = WebSession::getInstance()->getPrincipal();
      $username = $ppal->getName();

      $message = "User is not authorized - Authentication Error";
      $info = $ppal->isAnonymous() ? "Anonymous user" : '';

      $logger = Logger::getLogger("auth");
      $logger->info("{$_SERVER['SERVER_ADDR']}|{$_SERVER['REMOTE_ADDR']}|".LOG_APP_NAME."|LOGIN|114|{$message}|{$username}||||{$info}");

      //Throw exception to continue with predefined workflow
      throw $e;
    }

    try {
  	  $retVal = $this->performImpl(); 
      
      $this->logActionOK($this->getAction4Logger());

      return $retVal; 
    } catch (Exception $e) {
      $this->logActionERROR($this->getAction4Logger(), $e);

      throw $e;
    }
  }

  /**
   * Check the security to ensure this service can be method. 
   * Usually this method is overwritten.
   */
  public function checkSecurity() {
  }

  // --------------------------------------------------------------- Log Actions
  protected function logActionOK($action, $text='', $environment='', $objectType='', $objectId='') {
    $this->logAuth($action, '000', $text, $environment, $objectType, $objectId);
  }

  protected function logActionERROR($action, $exception, $environment='', $objectType='', $objectId='') {
    $this->logAuth($action, '001', get_class($exception) . ':' . $exception->getMessage(), $environment, $objectType, $objectId);
  }

  protected function logAuth($action, $outcome, $text='', $environment='', $objectType='', $objectId='') {
    if ( is_null($action) ) return;
    
    $ppal = WebSession::getInstance()->getPrincipal();
    $logger = Logger::getLogger("auth");

    $serverIp = $_SERVER['SERVER_ADDR'];
    $clientIp = $_SERVER['REMOTE_ADDR'];
    $userName = $ppal->isAnonymous() ? "anonymous" : $ppal->getLogin();

    $logger->info(
      $serverIp    . '|' .
      $clientIp    . '|' . 
      LOG_APP_NAME . '|' . 
      $action      . '|' . 
      $outcome     . '|' .
      $text        . '|' .
      $userName    . '|' . 
      $environment . '|' . 
      $objectType  . '|' . 
      $objectId    . '|' . 
      $this->getParamsAsString()
    );
  }

  protected function getAction4Logger() {
    return null;
  }

  protected function getParamsAsString() {
    return "";
  }

  // ---------------------------------------------------------- Abstract Methods
	/**
	 * Perform the specific business logic for this Service.
	 * 
	 * @return Array with the data
	 */
	protected abstract function performImpl();	
}
?>