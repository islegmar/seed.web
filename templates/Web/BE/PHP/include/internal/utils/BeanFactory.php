<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/utils/BeanNotFoundException.php');

class BeanFactory {
  public function newBean($className, $dirs) {
  	$logger = Logger::getLogger("main");
    
    // Search for this file in all folders
    $instance=null;
    foreach($dirs as $dir ) {
      // IL - 25/04/15 - We allow values in dir like '*/onegocio', allowing to load
      // Bean/onegocio/Bean.php
      $file = str_replace("*", $className, $dir)  . '/' . $className . '.php';
      
      if ( file_exists($file) ) {
        require_once($file);
      
        # IL - 05/11/13 - Allow names with /
        if ( strpos($className, '/')!==FALSE ) {
        	$tmp = explode("/", $className);
        	$className = $tmp[count($tmp)-1];
        }

        $instance=new $className();
        break; 
      }
    }

    if ( is_null($instance) ) {
    	throw new BeanNotFoundException('No implementation for "' . $className . '" found.');
    }

    return $instance;
  }
}
?>