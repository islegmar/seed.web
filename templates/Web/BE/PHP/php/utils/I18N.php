<?php
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');

/**
 * Custom version (for demo porpuses)
 * Load all the data form the database
 */
class I18N extends ConfigurableBean {
  // Current Language (we can set its value)
  protected $currLang = null;
  
	// We don't trough exceptions if we don't have translations
	protected $translations=array();
	
	/**
	 * Load the translations from a certain file
	 * @param unknown_type $lang
	 */
	public function load($file) {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('Load the translations from the DATABASE');
		}
		/*
		if ( !file_exists($file) ) {
			$this->logger->warn('File "' . $file . '" with translations does not exist.');
		} else {
			if ( is_dir($file) ) {
				$this->logger->warn('File "' . $file . '" with translations is a directory.');
			} else {
				$this->setTranslations(parse_ini_file($file));
			}
		}*/
		$allTrans = FactoryObject::newObject('_I18N')->findAll();
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('Found ' + count($allTrans) + ' translations.');
		}
		foreach ($allTrans as $row) {
			$key = $row['Name'];
			$value = $row['Text'];
		  $this->addTranslation($key, $value);
		}
	}
	/* Add one single translation */
	public function addTranslation($key, $val) {
		$this->translations[$key] = $val;
	}
	
	public function setTranslations($translations) {
		$this->translations = $translations;
	}
	
	public function getAllTranslations() {
		return $this->translations;
	}

	/**
	 * Get the file for a certain language or null if it is not defined
	 * @todo : ¿¿?? Does anybody use it outside, or it is only internal?
	 * 
	 * @param unknown_type $lang
	 */
	public function getFile($lang) {
		return $this->getOblCfgValue('filesDir') . '/' . $lang; 
	}
	
	/**
	 * Set the current lang. If it is not a supported lang, use the default one.
	 */
	public function setCurrLang($lang) {
	  // It is not a supported lang, use the efault
	  if ( is_null($lang) || !in_array($lang, $this->getCfgValue('supportedLangs', array())) ) {
	    // @todo : before we use the default, try to guess the language from the
	    // request
	    $this->currLang = $this->getDefLang();
	  } else {
	    $this->currLang = $lang;
	  }
	}
	
	/** 
	 * Get the current language. If not set, return the default
	 */
	public function getCurrLang() {
    // If have not set yet the currLang, try to guess it
	  if ( is_null($this->currLang) ) {
	    // @todo : avoid the use for LANG
  		global $LANG;
  		$this->setCurrLang(isset($LANG) ? $LANG : null);
	  } 
	  
	  return $this->currLang;
	}
	
	/**
   * Get the default language
	 */
	public function getDefLang() {
		return $this->getOblCfgValue('defLang');
	}
	
	public function translate($code, $vars=null, $values=null) {
		if ( is_null($vars) || is_null($values) ) {
			return isset($this->translations[$code]) ? $this->translations[$code] : $code;
		} else {
			return str_replace(
				$vars,
				$values,
				isset($this->translations[$code]) ? $this->translations[$code] : $code
			);
		}
	}
	
	// ---------------------------------------------------------- ConfigurableBean
	/**
	 * When configured, load the translations file
	 * @param unknown_type $cfg
	 */
	public function config($cfg) {
		parent::config($cfg);
		
		// Load the translations for the current language
		$fLang = $this->getFile($this->getCurrLang());
		// Not exists , use the default language
		if ( !file_exists($fLang) ) {
			$fLang = $this->getFile($this->getDefLang());
		} 
		
		// If file does not exist, is handled by load()
		$this->load($fLang);
	}
}
?>
