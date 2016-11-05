<?php
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');

/**
 * Generated a document based on a template oin OpenOffice
 * 
 * @author islegmar@gmail.com
 *
 */
class OdtDocGenerator extends ConfigurableBean {
  /**
   * Generate the document
   */
  public function generate($fileOdt, $fileXsl, $fileData, $dstFile=null) {
    $fileManager = FactoryObject::newObject('FileManager');

    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("generate($fileOdt, $fileXsl, $fileData, $dstFile)");
    }

    // Unzip the odt in a tmp folder
    $tmpDir = $fileManager->getTmpDir();     

    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("Unzip in $tmpDir");
    }

    $zip = new ZipArchive();
    if ($zip->open($fileOdt) !== TRUE) {
      throw new Exception("Cannot open <$fileOdt>");
    }
    if ( $zip->extractTo($tmpDir) !== TRUE ) {
      $zip->close();
      throw new Exception("Cannot extract <$fileOct> into <$dstDir>");
    }
    $zip->close();
  
    // Apply the xsl and generate a new version of content.xml
    rename($tmpDir . '/content.xml', $tmpDir . '/content.xml.orig');
    $xml = new DOMDocument();
    $xml->load($tmpDir . '/content.xml.orig');

    $xsl = new DOMDocument();
    $xsl->load($fileXsl);

    $proc = new XSLTProcessor();
    $proc->importStyleSheet($xsl);
    $proc->setParameter('', 'fData', $fileData);
    $proc->transformToURI($xml, $tmpDir . '/content.xml');
    unlink($tmpDir . '/content.xml.orig');
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("Xsl applied OK");
    }
    
    // Zip again in order to create the new odt
    $dstFile = is_null($dstFile) ? $fileManager->getTmpFileName() : $dstFile; 
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("Before zipping $tmpDir to create $dstFile...");
    }
    $this->zipData($tmpDir, $dstFile);
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("File $dstFile created OK.");
    }

    return $dstFile;
  }

  /**
   * Utility : all info about Odt and Xst is stored in _DocTemplate
   */
  public function generateFromDocTemplate($tmplName, $fileData, $dstFile=null) {
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("generateFromDocTemplate($tmplName, $fileData, $dstFile)");
    }

    $oDoc = FactoryObject::newObject('_DocTemplate');
    $oFile = FactoryObject::newObject('_File');
    $fileManager = FactoryObject::newObject('FileManager'); 

    $oDoc->loadByField('Name', $tmplName);
    
    // Template
    $idTemplate = $oDoc->getTemplate();
    $oFile->loadById($idTemplate);
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("Template>File with Id : " . $oFile->getId() . ", Path : " . $oFile->getPath());
    }
    $fileOdt=$fileManager->getAbsFilePath($oFile->getPath());
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("fileOdt : $fileOdt");
    }

    // Xsl
    $idXsl = $oDoc->getXsl();
    $oFile->loadById($idXsl);
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("Xsl>File with Id : " . $oFile->getId() . ", Path : " . $oFile->getPath());
    }
    $fileXsl=$fileManager->getAbsFilePath($oFile->getPath());
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug("fileXsl : $fileXsl");
    }

    return $this->generate($fileOdt, $fileXsl, $fileData, $dstFile);
  }

  // Utility : convert json to xml and save it in a termporary file
  public function getFileData($json_data) {
    // Contert the json in the XML
    $xml = FactoryObject::newObject('JsonUtils')->json2Xml($json_data);

    // Store this info in a temporary file
    $fileManager = FactoryObject::newObject('FileManager');
    $dstFile = $fileManager->getTmpFileName();
    $fileManager->storeFileWithFullPath($xml, $dstFile);

    return $dstFile;
  }

  // --------------------------------------------------------- Protected Methods 
  protected function zipData($source, $destination) {
    if (extension_loaded('zip')) {
      if (file_exists($source)) {
        $zip = new ZipArchive();
        if ($zip->open($destination, ZIPARCHIVE::CREATE)) {
          $source = realpath($source);
          if (is_dir($source)) {
            $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($source), RecursiveIteratorIterator::SELF_FIRST);
            foreach ($files as $file) {
              $file = realpath($file);
              if (is_dir($file)) {
                $zip->addEmptyDir(str_replace($source . '/', '', $file . '/'));
              } else if (is_file($file)) {
                $zip->addFromString(str_replace($source . '/', '', $file), file_get_contents($file));
              }
            }
          } else if (is_file($source)) {
            $zip->addFromString(basename($source), file_get_contents($source));
          }
        }
        return $zip->close();
      }
    }
    return false;
  }

  // ---------------------------------------------------------- ConfigurableBean
  /**
   * When configured, load the translations file
   * @param unknown_type $cfg
   */
  /*public function config($cfg) {
    parent::config($cfg);
    
    $this->symmetricKey = $this->getCfgValue('symmetricKey', null);
  }*/
}
?>
