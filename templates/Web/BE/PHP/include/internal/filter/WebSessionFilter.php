<?php
include_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/filter/IFilter.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');
// IMPORTANT (check http://efiquest.org/2007-12-10/6/ for +info)
// We need to include ALL classes (its real implementations) that are going
// to be referenced in WebSession (mainly the user) BEFORE we call getInstance
//require_once(INTERNAL_ROOT_DIR . '/security/AnonymousPrincipal.php');


/**
 * Represents a filter. Every project has its own WebSession object, so we 
 * don't have conflicts
 * 
 * @author islegmar
 *
 */
class WebSessionFilter implements IFilter {
	// ------------------------------------------------------------------- IFilter		
	public function exec($cfg) {
		$webSession = WebSession::getInstance($cfg['sessionName']);
		return true;
	}
}
?>