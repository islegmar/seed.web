<?php
/**
 * Load the data returned by Transformer 
 *
 * @TODO : does it have any sense that the Loader contains objects ILoad
 * as loader? Must this class perform any coordinate function as Transformer? 
 */
interface ILoader {
	public function config($config);

  /**
   * Load the data (fex. make it persistent in the database) provided by 
   * Transformer.
   */
	public function load($data);
}
?>