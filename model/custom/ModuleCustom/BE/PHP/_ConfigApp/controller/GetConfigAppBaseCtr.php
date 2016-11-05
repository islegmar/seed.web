<?php
require_once(INTERNAL_ROOT_DIR . '/controller/Controller.php');

/**
 * Base class with utility methods
 *
 * @author islegmar@gmail.com
 */
abstract class GetConfigAppBaseCtr extends Controller {
  protected function getFile($name) {
    $oFile = null;

    $cfg = FactoryObject::newObject('_ConfigApp')->getByField('IsActive', 1);

    if ( array_key_exists($name, $cfg) ) {
      try {
        $oFile = FactoryObject::newObject('_File')->loadById($cfg[$name]);
      // In case error, just return null
      } catch(Exception $e) { }
    }

    return $oFile;
  }
}
?>