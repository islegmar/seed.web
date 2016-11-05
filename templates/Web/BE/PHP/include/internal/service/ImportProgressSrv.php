<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');

/**
 * This service is called periodically from the client and provides information
 * about the progress of a certin Import proces (see ETLSrv)
 *
 * @author islegmar@gmail.com
 *
 */
class ImportProgressSrv extends Service {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    $notifyID = $this->getParamValue('notifyID', null);
    
    if ( !is_null($notifyID) && array_key_exists($notifyID, $_SESSION)) {
      return $_SESSION[$notifyID];
    } else {
      return array();
    }  
  }
}
?>
