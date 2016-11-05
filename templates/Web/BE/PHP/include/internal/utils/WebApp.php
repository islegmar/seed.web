<?php
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');

/**
 * It represents the web app : configuration, name ....
 * 
 * @author Isi
 *
 */
class WebApp extends ConfigurableBean {
	/**
	 * Apply all the filters for that request in order
   * Flow:
   * dispatcher.php : this is the main entry point and execute:
   * 1) config.php : one of the first thigs is to run 
   *                 applyFilters. If everything when fine the
   *                 execution continues.
   * 2) Initialize the controller and execute it
	 */
	public function applyFilters() {
		foreach ($this->getOblCfgValue('filters') as $filterName) {
			$filter = FactoryObject::newObject($filterName);
			if ( !$filter->exec()) {
				// If we don't exit, dispather.php is executed
				// @todo : review
				echo('Out in ' . $filterName);				
				exit;
			} 
		}
	}
}
?>
