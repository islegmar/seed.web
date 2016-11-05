<?php
/**
 * Extract data from a source and returns it to the Transformer, so it can be 
 * transformed.
 *
 * @TODO : does it have any sense that the Extractor contains objects IExtract
 * as loader? Must this class perform any coordinate function as Transformer? 
 */
interface IExtractor {

	public function config($config);

  /**
   * Returns an Object from a source of data.
   * If return null, that means there is no more data and the entire ETL process
   * must stop
   */
	public function extact();

  /**
   * Returns the total of records to process. If it returns null, means it can
   * not be calculatesd.
   */
  public function getTotalRecords();
}
?>