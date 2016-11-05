<?php
require_once(dirname(__FILE__) . '/__ConfigApp.php');

/**
 * _ConfigApp
 * IL - 01/06/16 : BEFORE the active instance is cached at request level (see config.php)
 * BUT because this is something that is in the database, it has been removed.
 */
class _ConfigApp extends __ConfigApp {
  public function loadActive() {
    $this->loadByField('IsActive', 1);      
    return $this;
  }
}
?>