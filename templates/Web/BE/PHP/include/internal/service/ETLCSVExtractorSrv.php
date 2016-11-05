<?php
require_once(INTERNAL_ROOT_DIR . '/service/ETLSrv.php');

/**
 * This is a common implementation, where the extactor get the data form a CSV file
 * 
 * @author islegmar@gmail.com
 *
 */
abstract class ETLCSVExtractorSrv extends ETLSrv {
  // -------------------------------------------------------------------- ETLSrv
  protected function getExtractor() {
    // Dissable by security reasons
    $file = null; //$this->params->getParam('file', null);  

    if ( is_null($file) ) {                            
      $file = $_FILES["fData"]["tmp_name"];            
    }                                                  

    if ( empty($file) ) {
      throw new Exception("No CSV file provided");
    }

    // Probably we have received extra params with aditional info used 
    // for importing the record. Fex. if we upload records for Child elements, 
    // we will receive as param the Id those records belongs to
    // @TODO : actually those params are not clear indentify in the request, so
    // will pass all of them :-(
    $values = $this->getAllParamsAsArray();


    $extractor = FactoryObject::newObject('ExtractorCSV');
    $extractor->config( 
      array(
        'file' => $file,
        'sep'  => $this->params->getParam('sepCSV','|'),
        'values' => $values
      )
    );

    return $extractor;
  }
}
?>
