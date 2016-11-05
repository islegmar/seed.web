<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');


/**
 * Set the actual language for the user
 * @TODO : I think currently is not in use
 *
 * @author islegmar@gmail.com
 *
 */
class SetLanguageSrv extends Service {
  // ------------------------------------------------------------------- Service
	protected function performImpl() {
    $lang = $this->params->getOblParam('lang');

    $webSession = WebSession::getInstance();
    $ppal= $webSession->getPrincipal();
    $ppal->setLanguage($lang);
    $webSession->update();
  
    return array();
	}
}
?>
