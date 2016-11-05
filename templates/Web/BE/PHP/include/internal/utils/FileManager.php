<?php
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');


/**
 * Handles the file system
 * 
 * @author islegmar@gmail.com
 */
class FileManager extends ConfigurableBean {
	public static $PARAM_DIR_BASE = 'dirBase';
	public static $PARAM_URL_BASE = 'urlBase';
	public static $PARAM_CREATE_MODE = 'createMode';
	public static $PARAM_TMP_DIR = 'tmpDir';
	
	// ---------------------------------------------------------- Public functions
	/**
	 * @param unknown_type $content
	 * @param unknown_type $relPath
	 * @return If this file can be accessed a URL, the url, otherwise null
	 * @throws Exception It the file or intermediate folders can not be created
	 */
	public function storeFile($content, $relPath) {
		$fileUrl = null;
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('storeFile(content=' . $content . 
					', relPath=' . $relPath . ')');
		}
		
		$urlBase = $this->getCfgValue(self::$PARAM_URL_BASE, null);
		if ( !is_null($urlBase) ) {
			$fileUrl = $urlBase . $relPath;
			if ( $this->logger->isDebugEnabled() ) {
				$this->logger->debug('fileUrl : ' . $fileUrl);
			}
		}
		
		$fullPath = $this->getOblCfgValue(self::$PARAM_DIR_BASE) . $relPath;
		
		$this->storeFileWithFullPath($content, $fullPath);
		
		/*
		$mode = intval($this->getCfgValue(self::$PARAM_CREATE_MODE, '0777'),8);
		$dir = dirname($fullPath);
		
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('fullPath "' . $fullPath . 
					'". Create dir "' . $dir . '" with mode "' . $mode . '"');
		}
		
		// Make all intermediate folders
		if ( !is_dir($dir) ) {
			if ( !mkdir($dir, $mode, true) ) {
				throw new Exception('Can not create dir "' . $dir . '" with mode "' . $mode . '"');
			}
		}
		
		if ( file_put_contents ($fullPath, $content)===FALSE ) {
			throw new Exception('Can not save in file "' . $fullPath . '"');
		}
		*/
		
		return $fileUrl;
	}
	
	/**
	 * Store a file in an absolute path. Here we don't return a url
	 * @param unknown_type $content
	 * @param unknown_type $relPath
	 * @throws Exception
	 */
	public function storeFileWithFullPath($content, $fullPath) {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('storeFileWithFullPath(content=' . $content . 
					', fullPath=' . $fullPath . ')');
		}

		$mode = intval($this->getCfgValue(self::$PARAM_CREATE_MODE, '0777'),8);
		$dir = dirname($fullPath);
		
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('fullPath "' . $fullPath . 
					'". Create dir "' . $dir . '" with mode "' . $mode . '"');
		}
		
		// Make all intermediate folders
		if ( !is_dir($dir) ) {
			if ( !mkdir($dir, $mode, true) ) {
				throw new Exception('Can not create dir "' . $dir . '" with mode "' . $mode . '"');
			}
		}
		
		if ( file_put_contents ($fullPath, $content)===FALSE ) {
			throw new Exception('Can not save in file "' . $fullPath . '"');
		}
	}
	
	public function getAbsFilePath($relPath, $createIntermediateFolders=false) {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('getFile(relPath=' . $relPath . 
					', createIntermediateFolders=' . $createIntermediateFolders . ')');
		}
		
		$fullPath = $this->getOblCfgValue(self::$PARAM_DIR_BASE) . $relPath;
		
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('fullPath "' . $fullPath . '"');
		}
		
		if ( $createIntermediateFolders ) {
			$dir=dirname($fullPath);
			// Check before if dir exists, otherwise we get an error!!
			if ( !file_exists($dir) ) {
	      // IL - 28/11/13 - Wrong, there was no conversion 		
				$mode = octdec($this->getCfgValue(self::$PARAM_CREATE_MODE, '0777'));
				if ( !mkdir($dir, $mode, true) ) {
					throw new Exception('Can not create dir "' . $dir . '" with mode "' . $mode . '"');
				}
								
				if ( $this->logger->isDebugEnabled() ) {
					$this->logger->debug('Create intermendiate folders "' . $dir . '"');
				}
			}  			
		}

		
		return $fullPath;
	}

	/**
	 * Check if a certain file exist
	 * @param unknown_type $relPath
	 * @param unknown_type $emptyIfNotExists
	 */
	public function existFile($relPath) {
		$file = $this->getAbsFilePath($relPath);
		
		return file_exists($file);
	}
	
	public function getFileContent($relPath, $emptyIfNotExists=false) {
		$file = $this->getAbsFilePath($relPath);
		if ( !file_exists($file) ) {
			if ( $emptyIfNotExists ) {
				return "";
			} else {
				throw new Exception('File "' . $file . '" does not exist.');
			}
		}
		
		return file_get_contents($file);
	}
  
  // IL - 28/11/13 - Get a temporary and unique folder where to put the stuff
	public function getTmpDir() {
  	// The base folder 
    $baseTmpDir = $this->getCfgValue(self::$PARAM_TMP_DIR, $this->getAbsFilePath('/tmpDir'));
    // Get a random id
    $randomID=substr(str_shuffle('abcdefghijklmnopqrstuvwxyz'),0, 10) . time();
    // The folder
    $tmpDir = $baseTmpDir . '/' . $randomID;
    
    // This should NEVER happen but the flies ....
    if ( file_exists($tmpDir) ) {
      throw new Exception('Temporary folder ' . $tmpDir . ' exists');
    }
    // Create intermediate folders
		$mode = octdec($this->getCfgValue(self::$PARAM_CREATE_MODE, '0777'));
		if ( !mkdir($tmpDir, $mode, true) ) {
      throw new Exception('Can not create dir "' . $tmpDir . '" with mode "' . $mode . '"');
		}
    
    return $tmpDir;
	}  

	// IL - 25/03/15 - Create a temporary file
  public function getTmpFileName($prefix='foo') {
  	// The base folder 
    $tmpDir = $this->getCfgValue(self::$PARAM_TMP_DIR, $this->getAbsFilePath('/tmpDir'));
    
    // Create if not exists
    if ( !file_exists($tmpDir) ) {
	    // Create intermediate folders
			$mode = octdec($this->getCfgValue(self::$PARAM_CREATE_MODE, '0777'));
			if ( !mkdir($tmpDir, $mode, true) ) {
	      throw new Exception('Can not create dir "' . $tmpDir . '" with mode "' . $mode . '"');
			}
    }
    
    return tempnam($tmpDir, $prefix);
	}	
}
?>