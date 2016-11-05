<?php
require_once(INTERNAL_ROOT_DIR . '/utils/Params.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/utils/BeanNotFoundException.php');

/**
 * Utility representing a web session. Takes care of Cache, User management and 
 * other funny stuff.
 * 
 * @todo : review the code, I'm not sure this $_SESSION / static is going to work....
 * This is a kind of singleton/session.....
 * 
 * NOTE : This is an special class that can not be instantiated via FactoryObject
 * 
 * @author Isi
 *
 */
class WebSession {
	private static $instance = NULL;
	private $sessionName;
	private $principal = null;
	
	// --------------------------------------------------------------- Constructor
	public static function getInstance($sessionName=null) {
		// IMPORTANT (check http://efiquest.org/2007-12-10/6/ for +info)
		// We need to include ALL classes (its real implementations) that are going
		// to be referenced in WebSession
		// Those classes are : Usuario, AnonymousPrincipal
		// A way to include them i create a dummy instance!!
		// IL - 06/07/13 - Beans opcionales
		try {
		$tmp = FactoryObject::newObject('AnonymousPrincipal');
		$tmp = FactoryObject::newObject('Usuario');
		} catch (BeanNotFoundException $e) {}
		
		@session_start();
		// Is already initiated in the same request?
		if(!isset(self::$instance)) {
			if ( is_null($sessionName) ) {
				throw new Exception('Not WebSession init before!');				
			} else {
				// Is already initiated in the same session?
				if ( isset($_SESSION[$sessionName])) {
					self::$instance = unserialize($_SESSION[$sessionName]);
				} else {
					// Create
					self::$instance = new WebSession();
					// and store it
					self::$instance->setSessionName($sessionName);
					self::$instance->update();
				}
			}
		}
		
		return self::$instance;
	}
	
	private function __construct() {
	}
	
	/**
	 * Autoupdate the session when exit!
	 * If we have changed any related object handled by the session (like the 
	 * principal) it will be automatically udapted on exit
	 * Removed because it is not very useful. We should auto-update any reference
	 */
	/*
	public function __destruct() {
		error_log("*************** __DESTRUCT WebSession");
		$this->update();
	}
	*/
	
	// ---------------------------------------------------------- Public functions
	public function update() {
		$_SESSION[$this->sessionName] = serialize($this);
	}
	
	public function setSessionName($sessionName) {
		$this->sessionName = $sessionName;
	}
	
	// --------------------------------------------------------- Getters & Setters
	public function getPrincipal() {
		return $this->principal;
	}
	
	/**
	 * Set a principal in the session. This method is called basically by:
	 * - Login and Logout Service
	 * - AnonymousUserFilter
	 * 
	 * @param IPrincipal $principal
	 */
	public function setPrincipal($principal) {
		@session_regenerate_id(true);
		$this->principal = $principal;
	}
}
?>
