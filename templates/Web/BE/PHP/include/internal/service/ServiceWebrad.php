<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/security/UserNotAuthenticatedException.php');

/**
 * Base servie the services for SeedWeb
 */
abstract class ServiceWebrad extends Service {
  /**
   * ALWAYS check the action permission, there is no way to overwrite that.
   */
  final public function checkSecurity() {
    $permission = $this->getPermissionNeeded();
    
    // It is NOT a public action
    if ( !empty($permission)) {      
      $ppal = $this->getPrincipal();
      // Not logged user. Throw this exception an usuarlly the fe will redirect
      // the request to the login page
      if ( $ppal->isAnonymous() ) {
        throw new UserNotAuthenticatedException();
      }

      // Check it the logged user has the needed permission
      FactoryObject::newObject('SecurityUtil')->checkPermission($permission);    
    } 

    // Check the custom security for this action (probably depending on the 
    // current state of the system)
    $this->checkSecurityImpl();
  }

  /**
   * By default, no specific checkSecurity is performed, but this method SHOULD
   * be overwritten by the derived class, so they can apply specific security
   * constraints.
   * @throws ActionDeniedException
   */
  protected function checkSecurityImpl() {
  }

  // --------------------------------------------------------- To be overwritten
  protected abstract function getPermissionNeeded();
}
?>
