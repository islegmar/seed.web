<?php
require_once(INTERNAL_ROOT_DIR . '/etl/IExtractor.php');

/**
 * In this implementation, the data is get from a CSV file.
 */
class ExtractorCSV implements IExtractor {
  // File name
  protected $fileName = null;
	protected $handlerFile = null;
	protected $sep = null;
  protected $values = null;

	// ---------------------------------------------------------------- IExtractor
	/**
	 * 'file' : the CSV's file name
	 * 'sep'  : the separator used in the CSV file 
	 */
	public function config($cfg) {
		$this->fileName = $cfg['file'];
		$this->sep = $cfg['sep'];
    $this->values = $cfg['values'];


    $this->handlerFile = fopen($this->fileName, "r");
    if ( $this->handlerFile===FALSE ) {
    	throw new Exception('File "' . $this->fileName . '" can not be read.');
    } 
	}

  /**
   * Returns the next line splitted
   */
	public function extact() {
    $data = fgetcsv($this->handlerFile, 10000, $this->sep);

    if ( $data===FALSE ) {
			fclose($this->handlerFile);
    	return null;
    }

    // @TODO : not sure if this is the nicest approach :-(. 
    // In case we have received extra values NOT with numeric index, add them
    if ( !empty($this->values) ) {
      $data = array_merge($data, $this->values);
    }

    return $data;
	}

  /**
   * Return the total of lines in the file
   */
  public function getTotalRecords() {
    $handle = fopen($this->fileName, "r");
    if ( $handle===FALSE ) {
      throw new Exception('File "' . $this->fileName . '" can not be read.');
    } 

    try {
      $linecount = 0;
      
      while(!feof($handle)){
        // Reads until the end of line is found. The only problem is a line is very 
        // long
        $line = fgets($handle);
        if ( !empty($line) ) {
          $linecount++;
        }
      }
      fclose($handle);
      
      return $linecount;
    } catch (Exception $e) {
      fclose($handle);
      throw $e;
    }
  }
}
