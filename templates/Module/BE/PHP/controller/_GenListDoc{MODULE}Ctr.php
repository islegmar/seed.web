<?php
require_once(INTERNAL_ROOT_DIR . '/controller/OdtDocGeneratorCtr.php');
require_once(INTERNAL_ROOT_DIR . '/db/DBConnectionManager.php');

/**
 * Generates a document with the list of {MODULE} - generated code
 */
class _GenListDoc{MODULE}Ctr extends OdtDocGeneratorCtr {
  protected $fTemplate;
  protected $fXsl;
  
  public function __construct() {
    parent::__construct();
    $oDoc = FactoryObject::newObject('_DocTemplate');
    $oFile = FactoryObject::newObject('_File');
    $fileManager = FactoryObject::newObject('FileManager'); 

    $oDoc->loadByField('Name', 'list');
    
    // Template
    $idTemplate = $oDoc->getTemplate();
    $oFile->loadById($idTemplate);
    $this->fTemplate=$fileManager->getAbsFilePath($oFile->getPath());

    // Xsl
    $idXsl = $oDoc->getXsl();
    $oFile->loadById($idXsl);
    $this->fXsl=$fileManager->getAbsFilePath($oFile->getPath());
  }
  
  //  ------------------------------------------------------- OdtDocGeneratorCtr
  protected function getPathTemplate() {
    return $this->fTemplate;
    //return "/home/ilegido/projects/20150005-newepbmanager-philippines/_OLD/files/reports/list.odt";
  }

  protected function getPathXsl() {
    return $this->fXsl;
    //return "/home/ilegido/projects/20150005-newepbmanager-philippines/_OLD/files/reports/list.xslt_create(oid)";
  }

  protected function getPathData() {
    $params = $this->getWebParams();
    
    // Get the data. To do dat, we execute again the List with the same parameters
    $srv = FactoryObject::newObject('ListaPaginableSrv');
    $srv->addParam('_object', $params->getParam('_list'));
    $srv->addParam('indPage', 0);
    $srv->addParam('totPerPage', 1000);
    $filter = [];
    foreach ($params->getAllParams() as $key => $value) {
      if ( $key!='controllerName' && $key!='_list' ) {
        $filter[$key] = $value;
      }
    }
    $srv->addParam('filter', $filter);
    
    $json_data = $srv->perform(DBConnectionManager::get())['data'];
    
    // Contert the json in the XML
    $xml='<?xml version="1.0" encoding="UTF-8"?>';
    $xml .= '<list>';
    $xml .= '<title>{MODULE}</title>';
    // TODO : What to do if there is no data?
    if ( count($json_data )>0 ) {
      // The column names
      $xml .= "<cols>";
      foreach ($json_data[0] as $name => $value) {
        // Not show the fields 'Id' and 'IdOwner' 
        if ( $name!='Id' && $name!='IdOwner' ) {
          $xml .= "<col>" . $name . "</col>";
        }
      }
      $xml .= "</cols>";

      // The rows with the values
      $xml .= "<data>";
      foreach ($json_data as $ind => $row) {
        $xml .= "<row>";
        foreach ($row as $name => $value) {
          // Not show the fields 'Id' and 'IdOwner' 
          if ( $name!='Id' && $name!='IdOwner' ) {
            // Encode the value, in case it contains symbols like & (eg. the 
            // files taht are returned as /webrad/be//action/GetFileDB?Id=4&fileName=Template-4)
            $xml .= "<" . $name . ">" . htmlentities($value) . "</" . $name . ">";
          } 
        }
        $xml .= "</row>";
      }
      $xml .= "</data>";      
    }
    $xml .= "</list>";

    // Store this info in a temporary file
    $fileManager = FactoryObject::newObject('FileManager');
    $dstFile = $fileManager->getTmpFileName();
    $fileManager->storeFileWithFullPath($xml, $dstFile);

    return $dstFile;
    // return "/home/ilegido/projects/20150005-newepbmanager-philippines/appEMS/model/data/files/reports/list.xml";
  }

  protected function getDocName() {
    return "List{MODULE}.odt";
  }
}
?>
