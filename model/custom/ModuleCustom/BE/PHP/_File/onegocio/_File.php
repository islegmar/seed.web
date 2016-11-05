<?php
require_once(dirname(__FILE__) . '/__File.php');

/**
 * _File
 * The file itself can be stored in the file system or in the database
 */
class _File extends __File {
  // @TODO : make it configurable
  protected $storeInDatabase = true;

  /**
   * @return String the content pointed by this file as string
   */
  public function getAsString() {
    if ( $this->storeInDatabase) {
      return $this->Content;
    } else {
      return FactoryObject::newObject('FileManager')->getFileContent($this->getPath());
    }
  }

  public function createInDatabase($pDb=null) {
    if ( $this->storeInDatabase ) {
      $this->setPath(null);
    // Keep in File System  
    } else {
      $path = '/' . md5($this->Content . '-' . microtime() . '-' . rand());
      FactoryObject::newObject('FileManager')->storeFile($this->Content, $path);
      if ( $this->logger->isDebugEnabled() ) {
        $this->logger->debug('path "' . $path . '"');
      }
      $this->setPath($path);
      $this->setContent(null);
    }

    parent::createInDatabase($pDb);
  }
}
?>