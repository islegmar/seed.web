<?php
require_once( INTERNAL_ROOT_DIR . '/controller/Controller.php'); 
require_once( INTERNAL_ROOT_DIR . '/controller/ServiceException.php'); 

/**
 * Executes some actions and return an ajax response
 *
 * @todo : very similar to Service ¿?
 * 
 * @author islegmar@gmail.com
 *
 */
abstract class AjaxController extends Controller {
	// ---------------------------------------------------------------- Controller
	public final function perform() {
		// IL - DO NOT CATCH TE EXCEPTION
		parent::perform();
		$response = json_encode($this->returnData());
		
		// Return the response
		if ( !is_null($response) ) {
			header('Content-type: application/json; charset=utf-8');
			echo $response;
		}
	}
	
	// ---------------------------------------------------------- Abstract Methods
	/**
	 * @return array with the data
	 */
	protected abstract function returnData();
}
?>
