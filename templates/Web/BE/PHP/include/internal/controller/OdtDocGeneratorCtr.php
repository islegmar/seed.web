<?php
require_once(INTERNAL_ROOT_DIR . '/controller/Controller.php');

/**
 * Generates and odt document using a template
 *
 * @author islegmar@gmail.com
 */
class OdtDocGeneratorCtr extends Controller {
  public function perform() {
    $file = FactoryObject::newObject('OdtDocGenerator')->generate(
      $this->getPathTemplate(),
      $this->getPathXsl(),
      $this->getPathData()
    );

    // Send the headers to foce download the zip file
    header("Content-type: application/vnd.oasis.opendocument.text"); 
    header("Content-Disposition: attachment; filename=" . $this->getDocName()); 
    header("Pragma: no-cache"); 
    header("Expires: 0"); 
    readfile($file);
  }

  // ------------------------------------------------------ Methods to Implement
  protected function getPathTemplate() {
    return $this->getWebParams()->$params->getParam('odtFile');
  }

  protected function getPathXsl() {
    return $this->getWebParams()->$params->getParam('xslFile');
  }

  protected function getPathData() {
    return $this->getWebParams()->$params->getParam('dataFile');    
  }

  protected function getDocName() {
    return "report.odt";
  }
}
?>