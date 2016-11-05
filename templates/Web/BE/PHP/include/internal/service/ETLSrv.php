<?php
require_once(INTERNAL_ROOT_DIR . '/service/ServiceWebrad.php');

/**
 * Applies an RTL transform. It uses:
 * - Extractor : get the data
 * - Tranformer : transform the data provided by Extractor
 * - Loader : do something with the transformed data provided by Extractor
 * 
 * So, basically it executes : loader(trasnformer(extractor()))
 * 
 * Thanks to : http://konrness.com/php5/how-to-prevent-blocking-php-requests/
 * for the session lock problem
 *
 * @author islegmar@gmail.com
 *
 */
abstract class ETLSrv extends ServiceWebrad {
  protected $notifyID = null;
  protected $totRecordsToImport = null;

	// ------------------------------------------------------------------- Service
	protected function performImpl() {
    @session_write_close();

    $this->writeProgress(0, 'start');

    $extractor = $this->getExtractor();
    $transformer = $this->getTransformer();
    $loader = $this->getLoader();

    // IMPORTANT : we do NOT allow chunks of import in order to keep the import
    // process without side effects and, if there is ANY error rollback
    // The only think we do is to inform to the client about the impor process

    // Check if we have received info from the client so we have notify periodically
    // about the probress
    $this->notifyID = $this->getParamValue('notifyID', null);

    $this->totRecordsToImport = $extractor->getTotalRecords();
    
    // Now, we will notify evry certain amount of records, depending on the 
    // total numbers of records
    $sizeBlock=null;
    if ( !is_null($this->totRecordsToImport) ) {
      if ( $this->totRecordsToImport<1000 ) {
        $sizeBlock=2;
      } else {
        $sizeBlock=1000;  
      }
    }      

    $this->logger->info('START. sizeBlock : ' . $sizeBlock . ', notifyID : ' . $this->notifyID . ', totRecordsToImport : ' . $this->totRecordsToImport . '.');

    $indTotal=0;
    $indBlock=0;
    while ( !is_null($data=$extractor->extact())) {
    	$loader->load($transformer->transform($data));
      ++$indTotal;
      
      // We have to info about the progress 
      if ( !is_null($sizeBlock) ) {
        ++$indBlock;
        if ( $indBlock===$sizeBlock ) {
          $this->logger->info('Processed ' . $indTotal . ' of ' . $this->totRecordsToImport . ' records ...');
          $indBlock=0;
        }

        // We have to notify to the client
        $this->writeProgress($indTotal);
      }
    }
    $this->writeProgress(0, 'done');

    $this->logger->info('Processed ' . $indTotal . ' records!');

    // When doing a big import that takes long, the process finishes fine BUT
    // in Chrome I get the error ERR_RESPONSE_HEADERS_TOO_BIG
    // Fater googling, I have found
    // http://stackoverflow.com/questions/17186675/why-i-get-err-response-headers-too-big-on-chrome
    header_remove('Set-Cookie');
    return array (
    	'totRecords' => $indTotal
    );
	}

  /**
   * Write the progress in the session, so the client can check the progress 
   * calling IMportProgressSrv.
   */
  protected function writeProgress($indTotal, $status='working') {
    if ( is_null($this->notifyID) ) return;

    // To avoid request locks
    @session_start();
    $_SESSION[$this->notifyID] = array(
      'indTotal' => $indTotal,
      'totRecordsToImport' => $this->totRecordsToImport,
      'time' => time(),
      'status' => $status
    );
    @session_write_close();
  } 

	// -------------------------------------------------------- Abstract Functions
  protected abstract function getExtractor();
  protected abstract function getTransformer();
  protected abstract function getLoader();
}
?>
