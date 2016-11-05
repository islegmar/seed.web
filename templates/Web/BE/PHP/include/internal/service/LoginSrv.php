<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');
require_once(INTERNAL_ROOT_DIR . '/security/CredentialLoginPwd.php');
require_once(INTERNAL_ROOT_DIR . '/security/UserNotFoundException.php');
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');

/**
 * Receives the credential (at this moment just login/pwd) and perform the login
 * (that means, put in the session a non anonymous user) 
 * 
 * @author islegmar@gmail.com
 *
 */
class LoginSrv extends Service {
  protected $cfg;

  // ------------------------------------------------------------------- Service
	protected function performImpl() {
	  // IL - 16/02/14 - If we have already received the credentials, don't try
	  // to make it
    // IL - 04/02/15 - use getParamValue instead
    $logger = Logger::getLogger("auth");
    $credential = $this->getParamValue('credential', null);
	  
	  // Use the default credentials implementation, UserPwd
	  if ( is_null($credential) ) {
      $credential = new CredentialLoginPwd();
      $credential->setLogin($this->getParamValue('login'));
      $credential->setPwd($this->getParamValue('password'));
	  }
    
    //echo('login : ' . $login . ', password : ' . $password);
    
    $serverIp = $_SERVER['SERVER_ADDR'];
    $clientIp = $_SERVER['REMOTE_ADDR'];
    $action = 'LOGIN';
    $username = $credential->getLogin();

    // Build the User Object
    $ppal = FactoryObject::newObject('Usuario');

    try {
      $ppal->authenticate($credential);
      $logger->info("{$serverIp}|{$clientIp}|".LOG_APP_NAME."|{$action}|000|Successful Authentication|{$username}||||");
      $ppal->setAnonymous(FALSE);

      // Store it!
      $webSession = WebSession::getInstance();
      $webSession->setPrincipal($ppal);
      $webSession->update();
    
      // Send where the user has to go.
      // We have three choices:
      // - The user iftself
      // - A value configured in default.php
      // - A default value
      $onLoginUrl = $ppal->getOnLoginUrl();
      // Not get the by the suer, try to get from the default config
      // and DO NOT use a default value, this means always problems ...
      if ( is_null($onLoginUrl) ) {
        $onLoginUrl = $this->getCfgValue('onLoginUrl');
      } 

      return array(
        'onLoginUrl' => $onLoginUrl
      );
      // IL - 03/03/15 - Remove the exit, why was before?
      //exit();
    // The authentication was not possible  
    } catch(Exception $e) {
      //throw new UserNotFoundException();
      $users = $ppal->getAllByField('Login', $username);

      //There is no user with that username
      $outcome = empty($users) ? 111 : 112 ;
      $message = empty($users) ? 'User do not exists - Authentication Error' : 'Password failure - Authentication Error';

      $logger->info("{$serverIp}|{$clientIp}|".LOG_APP_NAME."|{$action}|{$outcome}|{$message}|{$username}||||");
      return array('error' => 'NoUserFound');
    }
	}

  // ---------------------------------------------------------- ConfigurableBean
  public function config($cfg) {
    $this->cfg = $cfg;
  }

  public function getCfgValue($key, $default=null) {
    return isset($this->cfg[$key]) ? $this->cfg[$key] : $default;
  }

  public function getOblCfgValue($key) {
    if ( !isset($this->cfg[$key]) ) throw new Exception('Not exist param "' . $key . '"');

    return $this->getCfgValue($key);
  }
}
?>
