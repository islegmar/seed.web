<?php
require_once(INTERNAL_ROOT_DIR . '/controller/Controller.php');

/**
 * Get a a file from the Database (this works together with UploadFileDB)
 * 
 * INPUT
 * - Id : the _File.Id
 * 
 * @author islegmar@gmail.com
 *
 */
class GetFileDBCtr extends Controller {
	public function perform() {
		$idFile = $this->getWebParams()->getParam('Id');
    $fileName = $this->getWebParams()->getParam('fileName',$idFile);

    // Load the _File
    $oFile = FactoryObject::newObject('_File'); 
    $oFile->loadById($idFile);
    $content = $oFile->getAsString();
    
    // send the right headers
    if ( !is_null($oFile->getMimetype()) ) {
      header('Content-Type: ' . $oFile->getMimetype());
    }

    // @TODO : $content is a MySQL MEDIUMBLOB and with the current code
    // sizeof($content) returns alwasy 0 and the image is not shown 
    // header("Content-Length: " . sizeof($content));
    if ( !is_null($oFile->getFileName()) ) {
      header("Content-Disposition: attachment; filename=" . $oFile->getFileName()); 
    }

    echo($content);
  }
}
?>