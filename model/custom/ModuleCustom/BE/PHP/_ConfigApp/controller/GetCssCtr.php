<?php
require_once(INTERNAL_ROOT_DIR . '/controller/Controller.php');
require_once(APP_ROOT_DIR . '/_ConfigApp/controller/GetConfigAppBaseCtr.php');

/**
 * Returns the specific css
 *
 * @author islegmar@gmail.com
 */
class GetCssCtr extends GetConfigAppBaseCtr {
  public function perform() {
    $oFile = $this->getFile('Css');
    // Send always something to avoid errors in the client side when there is no
    // custom css
    header("Content-type: text/css"); 
    if ( !is_null($oFile) ) {
      // Send the logo
      // header("Pragma: no-cache"); 
      // header("Expires: 0"); 
      echo $oFile->getAsString();      
    }
  }
}
?>