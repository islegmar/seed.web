<?php
/**
 * Base clase for all the beans that receives a configuration
 * 
 * @todo : is an utility class that I'm not sure if it is very useful
 * 
 * @author islegmar@gmail.com
 */
class ConfigurableBean {
	protected  $logger;
	protected $cfg;
	
	// --------------------------------------------------------------- Constructor
	public function __construct() {
		$this->logger = Logger::getLogger("main");
	}
	
	// ---------------------------------------------------------- Public functions
	public function config($cfg) {
		$this->cfg = $cfg;
	}

	public function getCfgValue($key, $default=null) {
		return isset($this->cfg[$key]) ? $this->cfg[$key] : $default;
	}
	
	public function getOblCfgValue($key) {
		if ( !isset($this->cfg[$key]) ) throw new Exception('Not exist param "' . $key . '"');
		
		return $this->getCfgValue($key);
	}
}
?>
