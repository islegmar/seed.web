<?php
require_once(INTERNAL_ROOT_DIR . '/controller/Controller.php');
require_once(APP_ROOT_DIR . '/_ConfigApp/controller/GetConfigAppBaseCtr.php');

/**
 * Returns the logo
 *
 * @author islegmar@gmail.com
 */
class GetLogoCtr extends GetConfigAppBaseCtr {
  public function perform() {
    $oFile = $this->getFile('Logo');
    if ( !is_null($oFile) ) {
      // Send the logo
      // header("Content-type: application/vnd.oasis.opendocument.text"); 
      // header("Content-Disposition: attachment; filename=" . $this->getDocName()); 
      // header("Pragma: no-cache"); 
      // header("Expires: 0"); 
      echo $oFile->getAsString();      
    }
  }
}
?>