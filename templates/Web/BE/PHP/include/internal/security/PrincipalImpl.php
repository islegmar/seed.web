<?php
require_once (INTERNAL_ROOT_DIR . '/security/IPrincipal.php');
require_once (INTERNAL_ROOT_DIR . '/security/ICredential.php');

/**
 * Basic implementation of IPrincipal
 * 
 * @author islegmar
 *
 */
class PrincipalImpl implements IPrincipal {
	private $name;
	private $anonymous;
	private $language;
	
	/**
	 * Create constructor to avoid errors when child call parent::__construct
	 */
	public function __construct(){
	}
	
	// ---------------------------------------------------------- Public Functions 
	public function setName($name) {
		$this->name = $name;
	}
	
	public function setAnonymous($anonymous) {
		$this->anonymous = $anonymous;
	}
	
	public function setLanguage($language) {
		$this->language = $language;
	}
	
	// ----------------------------------------------------------------- Principal
	public function getName() {
		return $this->name;
	}
	
	public function isAnonymous() {
		return $this->anonymous;
	}

	public function getLanguage() {
		return $this->language;
	}
	
	// IL - 13/11/13
	public function authenticate(ICredential $credential) {
	}
}