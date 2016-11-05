<?php
require_once ( INTERNAL_ROOT_DIR . '/security/ICredential.php');

/**
 * Represents a principal in the system.
 * @author islegmar
 *
 */
interface IPrincipal {
	public function getName();
	public function getLanguage();
	public function isAnonymous();
	// IL - 13/11/13 - Added the authenticate method
	public function authenticate(ICredential $credential);
}
?>