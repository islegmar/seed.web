<?php
require_once(INTERNAL_ROOT_DIR . '/utils/WebParams.php');
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');
require_once(INTERNAL_ROOT_DIR . '/db/DBConnectionManager.php');

error_reporting(E_ALL);
// ini_set('display_errors', 'stderr');
// @TODO : we should make configurable to set the right timezone, other
// wise the dates are not shown properly when transforming to strings
// date_default_timezone_set('Europe/Madrid');

/** 
 * A request's flow is the following:
 * dispatcher.php (custom)
 * |-> config.php (custom)
 * |-> Dispatcher.php (standard, this file)
 * 
 * For the Exception handling see http://www.php.net/manual/en/class.errorexception.php
 * @author islegmar
 *
 */
class Dispatcher extends ConfigurableBean {
  protected $logger;
  
  /**
   * Dispatch this request; that means locate an appropiate controller and
   * execute it.
   */
  public function dispatch() {
    $controller = null;
    try {
      $logger = Logger::getLogger("main");

      // -------------------------------------------------------- Get Parameters
      $WEB_PARAMS = new WebParams(); 
      $controllerName = $WEB_PARAMS->getOblParam('controllerName');
      
      // ------------------------------------------ Get the controller & Execute
      if ( $logger->isDebugEnabled() ) {
  	    $logger->debug('Invocando controller [' . $controllerName . ']');  
      }
  
      // We do this, so if there is any error I can set the header
      ob_start();
      // This is going to write in the output (it can be a web page, a JSON,...)
      $controller = FactoryObject::newObject($controllerName);  
      // IL - 02/03/2015 - In case we want to go somewhere after the job 
      $url = $controller->perform();
  
      // Commit, if any db connection
      DBConnectionManager::commit();
      ob_end_flush();
      if ( gettype($url)!='NULL' ) {
        header('Location : ' . $url);  
      }
    // A) An Exception has been thrown in the code. 
    // B) A warning, notice,..... has been produced in the code. In this case, 
    // it goes to err_handler, that throws an exception that is catched here
    } catch (Exception $error) {
	    DBConnectionManager::rollback();
	    
	    // Ok, if the error thrown comes from an ajax call, set the right header
	    // to show th message
	    require_once(INTERNAL_ROOT_DIR . '/controller/AjaxController.php');
	    
      // Return ALWAYS 200
	    if ( !is_null($controller) && $controller instanceof AjaxController ) {
  	    require_once(INTERNAL_ROOT_DIR . '/BeanValidateException.php');
	      
  	    header('Content-type: application/json; charset=utf-8');
        header( 'HTTP/1.0 200 ');
        // Controled error
        if ( $error instanceof BeanValidateException ) {
          echo(json_encode(array('errors' => $error->getErrors())));
        // Unexpeted error
        } else {
          $loggerError = Logger::getLogger("error");
          $loggerError->error($error);
          
  	      echo(json_encode(array('errors' => array('generic'=>'UnexpectedServerError'))));
      	}
	    // It is another kind of error, log the error but do NOT return any 
      // info that could be exploited by the caller   
	    } else {
      	// Log error
      	$loggerError = Logger::getLogger("error");
       	$loggerError->error($error);
    	
   	    header( 'HTTP/1.0 500');
	    }
    }	 
  }
}?>