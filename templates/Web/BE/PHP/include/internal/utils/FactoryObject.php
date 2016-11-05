<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/utils/BeanFactory.php');


/**
 * Generates instance of objects
 * Before was singleton, but now has changed to pure static
 * 
 * @author islegmar@gmail.com
 */
class FactoryObject {
	private static $cfg;
	// 'Singleton' beans that have been already instantiated
	private static $singletons = array();
	
	// ---------------------------------------------------------- Public functions
	public static function config($cfg) {
		FactoryObject::$cfg = $cfg;
	}
	
	/**
	 * Return the instance of an obejct
	 * @param $objId The object id
	 */
	public static function newObject($objId) {
		$logger = Logger::getLogger("main");
		
		/*if ( $logger->isDebugEnabled() ) {
			$logger->debug('newObject(' . $objId . ')');	
		}*/ 
		
		// Has been this bean already instantiated
		if ( isset(FactoryObject::$singletons[$objId]) ) {
			return FactoryObject::$singletons[$objId];
		} else {
			// This object is registered as a bean
			if ( isset(FactoryObject::$cfg['beans'][$objId])) {
				$params = FactoryObject::$cfg['beans'][$objId];
				$obj = null;
				
				$file  = $params['file'];
				$class = $params['class'];
				
				/*if ( $logger->isDebugEnabled() ) {
					$logger->debug('Found as bean. file "' . $file . '", class "' . $class . '"');	
				}*/ 
				
				require_once $file;
				$obj = new $class();
				
				// Configure it
				if ( isset($params['cfg']) ) {
					// @todo : instead of using this special method 'config', call the
					// corresponfig set<ParamName>() but, is this slow?
					$obj->config($params['cfg']);
				}
				
				// If this object is marked as singleton, keep it
				if ( isset($params['singleton']) && $params['singleton']==TRUE ) {
					// IL - 27/11/13 - Super weird!!!!! This line, keeping the singleton
					// was missing. Then, how could never then method hasBeenAlreadyInstantiated
					// worked??
					FactoryObject::$singletons[$objId]=$obj;
					/*if ( $logger->isDebugEnabled() ) {
						$logger->debug('bean "' . $class . '" is marked as singleton.');	
					}*/ 
				}
				
				// Return the object
				return $obj;
			// Try to find in the list of dirs	
			} else {
				/*if ( $logger->isDebugEnabled() ) {
					$logger->debug('Search in the list of dirs');
				}*/ 
				
				$beanFactory = new BeanFactory();
				return $beanFactory->newBean($objId, FactoryObject::$cfg['dirs']);
			}
		}
	}
	
	// IL - 21/11/13 - Check if a sigleton object has been already instantiated
	// (used basically for DBConenction that performs automatically some actions 
	// when instantiated)
	public static function hasBeenAlreadyInstantiated($objId) {
		return isset(FactoryObject::$singletons[$objId]);
	}
}
?>
