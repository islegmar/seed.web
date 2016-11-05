<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FileManager.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FileUtils.php');

/**
 * Save a file in the DB (and the contents in the database)
 * 
 * @author islegmar@gmail.com
 *
 */
class UploadFileDBSrv extends Service {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    // @TODO : It $this->getParamValue('content') raises an error because 
    // $this->params is null. It is not clear when the params are set, so 
    // we will get from POST
		$base64Content = $_POST['content'];

		// Decode this file (and get extra info)
		$info = FileUtils::decodeBase64($base64Content);		
		$mimetype = $info['mimetype'];
		$content  = $info['content'];
		
    // @TODO : In order to be more generic, the decission about where store the 
    // file (in File System or Database) shpudl  be is should be performed by
    // class _File 
		
		// Save the file. _File will take care of saving the file in the file system
    // or in the database
		$oFile = FactoryObject::newObject('_File');
    $oFile->setMimetype($mimetype);
    $oFile->setContent($content);
    $oFile->createInDatabase();

    // The JS expects to find the attribute 'url' that will the value we will use 
    // to store the file's value. 
		return array(
			'url' => $oFile->getId()
		);
	}
}
?>