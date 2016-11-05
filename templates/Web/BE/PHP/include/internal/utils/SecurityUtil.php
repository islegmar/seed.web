<?php
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');

/**
 * Several utilities
 * 
 * @author islegmar@gmail.com
 *
 */
class SecurityUtil  {
  /**
   * Check if the current user has any of the roles specified.
   * @TODO : this should be removed in favour checkPermission
   * @para $roles Array of role names.
   */
  public function checkPrincipalRoles($listRoleNames) {
    $ppal = WebSession::getInstance()->getPrincipal();                 
                                                                     
    // No role restriction                                             
    if ( empty($listRoleNames) ) return;                                       
                                                                     
    // If there is any role restriction, that means the anonymous      
    // users do not have access                                        
    if ( $ppal->isAnonymous() ) {                                      
      throw new Exception('Anonymous user can not access');            
    }                                                                  
                                                                     
    // Cheeck if this authenticated user has access                    
    if ( !$ppal->hasRole($listRoleNames) ) {                                   
      throw new Exception('Authenticated user has not the required role');                                                                    
    }                                                                  
  }           

  /**
   * Check if the current user has a certain Permission
   * @para $permissionName String 
   */
  public function checkPermission($permissionName) {
    $ppal = WebSession::getInstance()->getPrincipal();                 
                                                                     
    // No role restriction                                             
    if ( empty($permissionName) ) return;                                       
                                                                     
    // If there is any role restriction, that means the anonymous      
    // users do not have access                                        
    if ( $ppal->isAnonymous() ) {                                      
      throw new Exception('Anonymous user can not access');            
    }                                                                  
                                                                     
    // Cheeck if this authenticated user has access                    
    if ( !$ppal->hasPermission($permissionName) ) {                                   
      throw new Exception('Authenticated user has not the required permission');                                                                    
    }                                                                  
  }           
}
?>
