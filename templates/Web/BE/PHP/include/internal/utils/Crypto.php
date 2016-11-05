<?php
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');

/**
 * A VERY LIMITED crypto utilities 
 * 
 * @author islegmar@gmail.com
 *
 */
class Crypto extends ConfigurableBean {
  protected $symmetricKey=null;

  /**
   * Returns an encrypted & utf8-encoded
   */
  function encryptSymmetric($pure_string, $encryption_key=null) {
    if ( is_null($encryption_key) ) $encryption_key=$this->symmetricKey;

    $iv_size = mcrypt_get_iv_size(MCRYPT_BLOWFISH, MCRYPT_MODE_ECB);
    $iv = mcrypt_create_iv($iv_size, MCRYPT_RAND);
    $encrypted_string = mcrypt_encrypt(MCRYPT_BLOWFISH, $encryption_key, utf8_encode($pure_string), MCRYPT_MODE_ECB, $iv);
    return $encrypted_string;
  }

  /**
   * Returns decrypted original string
   */
  function decryptSymmetric($encrypted_string, $encryption_key=null) {
    if ( is_null($encryption_key) ) $encryption_key=$this->symmetricKey;
    
    $iv_size = mcrypt_get_iv_size(MCRYPT_BLOWFISH, MCRYPT_MODE_ECB);
    $iv = mcrypt_create_iv($iv_size, MCRYPT_RAND);
    $decrypted_string = mcrypt_decrypt(MCRYPT_BLOWFISH, $encryption_key, $encrypted_string, MCRYPT_MODE_ECB, $iv);
    // TODO : the returned string can contain paddigns (spaces) and new lines?
    return trim($decrypted_string);
  }

  // ---------------------------------------------------------- ConfigurableBean
  /**
   * When configured, load the translations file
   * @param unknown_type $cfg
   */
  public function config($cfg) {
    parent::config($cfg);
    
    $this->symmetricKey = $this->getCfgValue('symmetricKey', null);
  }
}
?>
