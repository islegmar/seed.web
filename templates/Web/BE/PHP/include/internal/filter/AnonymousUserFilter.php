<?php
include_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/filter/IFilter.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');

/**
 * Ensure we have ALWAYS in the session a user.
 * If there is no logged user, we put an anonymous one.
 * 
 * @author islegmar
 *
 */
class AnonymousUserFilter extends ConfigurableBean implements IFilter {
	// ------------------------------------------------------------------- IFilter		
	public function exec() {
		$webSession = WebSession::getInstance();
		$ppal = $webSession->getPrincipal();
		// If no user is created, set an anonymous user
		if ( is_null($ppal) ) {
			$ppal = FactoryObject::newObject('AnonymousPrincipal');
			// IL - 13/11/13 - Be sure it's marked as anonymous
			$ppal->setAnonymous(true);
			$webSession->setPrincipal($ppal);
		
			$webSession->update();
		}
		return true;
	}
}
?>