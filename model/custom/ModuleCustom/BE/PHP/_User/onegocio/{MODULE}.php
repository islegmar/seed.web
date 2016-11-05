<?php
require_once(dirname(__FILE__) . '/_{MODULE}.php');
require_once (INTERNAL_ROOT_DIR . '/security/IPrincipal.php');
require_once (INTERNAL_ROOT_DIR . '/security/ICredential.php');
require_once (INTERNAL_ROOT_DIR . '/security/CredentialLoginPwd.php');
require_once (APP_ROOT_DIR . '/_Role/onegocio/_Role.php');
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');

/**
 * {MODULE}
 *
 * @author islegmar@gmail.com
 */
class {MODULE} extends _{MODULE} implements IPrincipal {
  private $anonymous;
  // @TODO : If RBAC, add in IPrincipal
  protected $role = null; // Object _Role

  // -------------------------------------------------------------------- __User
  public function getAsArray($pData=null) {
    $data = parent::getAsArray($pData);
    $data['permissions'] = is_null($this->getId()) ? array() : $this->getPermissions();
    $data['role'] = $this->getRoleName();

    return $data;
  }

  public function getOnLoginUrl() {
    if ( !is_null($this->OnLoginUrl) ) {
      return $this->OnLoginUrl;
    } else {
      if ( !is_null($this->role) ) {
        return $this->role->getOnLoginUrl();
      } else {
        return null;
      }
    }
  }
  
  // ---------------------------------------------------------------- IPrincipal
  public function getName() {
    return $this->getLogin();
  }

  public function getLanguage() {
    return "ca";
  }

  public function isAnonymous() {
    return $this->anonymous;
  }

  public function authenticate(ICredential $credential) {
    if ( $credential instanceof CredentialLoginPwd ) {
      $sql = <<<EOD
      SELECT _User.*
        FROM _User
        JOIN _UserStatus
          ON _UserStatus.Id = _User.Id_UserStatus 
       WHERE _User.Login      = :Login
         AND _User.Password   = :Password
         AND _UserStatus.Name = 'ACTIVE'
EOD;
      $this->findOneWithStmt($sql, array(
        ':Login' => $credential->getLogin(), 
        ':Password' => $credential->getPwdPbkdf2()
      ), true);

      $this->role = FactoryObject::newObject("_Role");
      $this->role->loadById($this->getId_Role());
    } else {
      throw new Exception('Unsupported authentication method');
    }
  }

  public function logout() {
    $webSession = WebSession::getInstance();
    $webSession->setPrincipal(null);
    $webSession->update();
  }

  // @TODO : add in IPrincipal
  public function setAnonymous($anonymous) {
    $this->anonymous = $anonymous;
  }

  public function getRoleName() {
    return $this->role->getName();
  }

  public function hasRole($role) {
    return is_string($role) ? $this->role->getName()==$role : in_array($this->role->getName(), $role);  
  }

  public function hasPermission($permissionName) {
    return empty($permissionName) || $this->role->hasPermission($permissionName);
  }

  // Return an array with all the permissions
  public function getPermissions() {
    if ( is_null($this->role) ) {
      $this->role = FactoryObject::newObject("_Role");
      $this->role->loadById($this->getId_Role());
    }
    
    return $this->role->getPermissions();
  }

  /** 
  * Register the user:
  * + Create in the database
  * + Send the activation e-mail
  */
  public function register($clearPwd, $sendActivationEmail=True ) {
    // ---------------------------------------------------------------- Password
    $credentialLoginPwd = FactoryObject::newObject('CredentialLoginPwd');
    $credentialLoginPwd->setLogin($this->getLogin());
    $credentialLoginPwd->setPwd($clearPwd);
    $newPwd = $credentialLoginPwd->getPwdPbkdf2();
    $this->setPassword($newPwd);

    // --------------------------------------------------------- Activation Email
    if ( $sendActivationEmail ) {
      $this->setActivationCode(md5($this->getLogin() . @time()));
      
      // We need to compute the full URL to activate the credential. In a first
      // approach we get it from the request uri, with some search& replace, but
      // those things are always a problem, so now we have to set the base URL as
      // a configuration parameter
      $cfgApp = FactoryObject::newObject('_ConfigApp')->loadActive();

      $url = $cfgApp->getBaseURL() . '/fe/_User/ActivateAccount_User.html';
      $url .= '?ActivationCode=' . $this->getActivationCode();
      FactoryObject::newObject('_MailTemplate')
        ->loadByField('MID', '_User:Register')
        ->sendEmail(
            $this->getEmail(), 
            array(
              '$url'  => $url,
              '$name' => $this->getLogin()
            )
          );
    }

    // --------------------------------------- Finally, register in the database  
    $this->createInDatabase();  
  }
}
?>
