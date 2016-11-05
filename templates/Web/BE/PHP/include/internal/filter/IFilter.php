<?php

/**
 * Represents a filter.
 * 
 * They receive the configuration (if any) as any other bean, through FactoryObject
 * (for this reason usually the filters extend ConfigurableBean, but I prefere
 * 
 * @author islegmar
 *
 */
interface IFilter {
	/**
	 * @return true if the next filter can be applied, false to stop
	 */
	public function exec();
}
?>