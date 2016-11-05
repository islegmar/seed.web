<?php
require_once(INTERNAL_ROOT_DIR . '/security/PrincipalImpl.php');

class MyUsuario extends PrincipalImpl {
  public function authenticate(ICredential $credential) {
  }
 
  # For anonymous, return True only if the list is empty
  public function hasRole($role) {
    return empty($role);
  }

  public function getRoleName() {
    return "";
  }

  public function hasPermission($permissionName) {
    return empty($permissionName);
  }
}
?>
