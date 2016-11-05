<?php
require_once(INTERNAL_ROOT_DIR . '/security/ICredential.php');

/**
 * Use login/pwd as credentials
 * 
 * @author islegmar
 *
 */
class CredentialLoginPwd implements ICredential {
	private $login = null;
  private $pwd = null;
  
  // --------------------------------------------------------- Setters & Getters
  public function setLogin($login) {
    $this->login = $login;  
  }
  
  public function getLogin() {
    return $this->login;  
  }

  public function setPwd($pwd) {
    $this->pwd = $pwd;  
  }
  
  public function getPwd() {
    return $this->pwd;  
  }

  // ------------------------------------------------------------ Public Methods
  // Get the transformed password
  public function getPwdPbkdf2() {
    return hash_pbkdf2 ( "sha256", $this->pwd, $this->login, 1000, 60);
  }
}
?>