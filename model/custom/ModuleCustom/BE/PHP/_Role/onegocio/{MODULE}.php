<?php
require_once(dirname(__FILE__) . '/_{MODULE}.php');

/**
 * {MODULE}
 *
 * @author islegmar@gmail.com
 */
class {MODULE} extends _{MODULE} {
  protected $allPermissions = null;

  /* Check if current role has a certain permission */
  public function hasPermission($permissionName) {
    return in_array($permissionName, $this->getPermissions());
  }

  public function getPermissions() {
    // If the permissions have not been loaded, load them
    // For eficientcy, we will just store the names, not the objects
    if ( is_null($this->allPermissions) ) {
      $tmpRole = FactoryObject::newObject("_Permission");
      $this->allPermissions = $tmpRole ->getAllPermissionByIdRole($this->getId());
    } 

    return $this->allPermissions;
  }

}
?>
