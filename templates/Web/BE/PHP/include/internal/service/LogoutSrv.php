<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');

/**
 * Remove the current user from the session
 *
 * @author islegmar@gmail.com
 */
class LogoutSrv extends Service {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    $webSession = WebSession::getInstance();

    $logger = Logger::getLogger("auth");
    // Build the User Object
    $ppal = $webSession->getPrincipal();
    $userName = $ppal->getName();
    $ppal->logout();
    $logger->info("{$_SERVER['SERVER_ADDR']}|{$_SERVER['REMOTE_ADDR']}|".LOG_APP_NAME."|LOGOUT|000|Successful Logout|{$userName}||||");

    $webSession->setPrincipal(null);
    $webSession->update();
  
    // @TODO : refractor the use of WebSession as alternative to _SESSION. 
    // Probably a logout does not mean to destroy sessio0n if we only use
    // WebSession but we can not guarantee that, so destroy the session when 
    // logout
    // Just session_destroy it does not unset any of the global variables 
    // associated with the session, or unset the session cookie. ...  
    // http://stackoverflow.com/questions/8641929/session-destroy-not-unsetting-the-session-id
    @session_unset();
    @session_destroy();
    @setcookie("PHPSESSID", "", 1);
    @session_start();
    @session_regenerate_id(true);

    return array();
  }
}
?>
