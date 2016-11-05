<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/utils/BeanFactory.php');


/**
 * Generates the instance of a service based on its name and version
 * 
 * @author islegmar@gmail.com
 *
 */
class ServiceFactory {
  public function newService($service) {
    $dirs = array();
    if ( @!is_null(APP_ROOT_DIR) ) {
      array_push($dirs, APP_ROOT_DIR . '/php/service');    
    }
    array_push($dirs, dirname(__FILE__));    

    $factory = new BeanFactory(); 
    return $factory->newBean($service, $dirs);
  }
}
?>
